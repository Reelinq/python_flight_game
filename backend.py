import mysql.connector
import math

SETTINGS = {
	"initial_co2_budget": 2000,
	"co2_per_100km": 20
}

class GameState:
    def __init__(self, screen_name: str, start_airport_ident: str, co2_budget: float, target_airports: list[dict]):
        self.screen_name = screen_name
        self.location = start_airport_ident
        self.co2_budget = float(co2_budget)
        self.co2_consumed = 0.0
        # Store a copy so callers cannot mutate internal state accidentally
        self.target_airports = [airport.copy() for airport in target_airports]
        self._visited_target_idents: set[str] = set()

    @property
    def remaining_budget(self) -> float:
        return self.co2_budget - self.co2_consumed

    @property
    def remaining_targets(self) -> list[dict]:
        return [airport for airport in self.target_airports if airport["ident"] not in self._visited_target_idents]

    @property
    def targets_completed(self) -> int:
        return len(self._visited_target_idents)

    def record_travel(self, destination_ident: str, co2_spent: float) -> bool:
        self.co2_consumed += co2_spent
        self.location = destination_ident

        for airport in self.target_airports:
            if airport["ident"] == destination_ident and destination_ident not in self._visited_target_idents:
                self._visited_target_idents.add(destination_ident)
                return True
        return False

    def to_dict(self) -> dict:
        return {
            "screen_name": self.screen_name,
            "location": self.location,
            "co2_budget": self.co2_budget,
            "co2_consumed": self.co2_consumed,
            "remaining_budget": self.remaining_budget,
            "target_airports": [airport.copy() for airport in self.target_airports],
            "remaining_targets": [airport.copy() for airport in self.remaining_targets],
            "targets_completed": self.targets_completed,
        }


CURRENT_GAME: GameState | None = None

def get_connection():
	return mysql.connector.connect(
	host="localhost",
	user="root",
	password="2006",
	database="flight_game"
)

def haversine(start_lat, start_lon, end_lat, end_lon):
	EARTH_RADIUS_KM = 6371

	start_lat_rad = math.radians(start_lat)
	end_lat_rad = math.radians(end_lat)
	lat_diff = math.radians(end_lat - start_lat)
	lon_diff = math.radians(end_lon - start_lon)

	a = (math.sin(lat_diff / 2) ** 2 +
		 math.cos(start_lat_rad) * math.cos(end_lat_rad) *
		 math.sin(lon_diff / 2) ** 2)

	central_angle = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

	return EARTH_RADIUS_KM * central_angle

def co2_cost_km(distance_km):
	per_km = SETTINGS["co2_per_100km"] / 100.0
	return distance_km * per_km

def get_airport(ident):
	conn = get_connection()
	cur = conn.cursor(dictionary=True)
	cur.execute("SELECT ident, name, municipality, iso_country, latitude_deg, longitude_deg FROM airport WHERE ident=%s", (ident,))
	airport = cur.fetchone()
	cur.close()
	conn.close()
	return airport

def search_airports(search_term, limit=10):
	conn = get_connection()
	cur = conn.cursor(dictionary=True)
	search_pattern = f"%{search_term}%"
	cur.execute("""
		SELECT ident, name, municipality, iso_country
		FROM airport
		WHERE (name LIKE %s OR municipality LIKE %s OR ident LIKE %s)
		AND type IN ('large_airport', 'medium_airport')
		ORDER BY
			CASE
				WHEN ident LIKE %s THEN 1
				WHEN name LIKE %s THEN 2
				ELSE 3
			END,
			name
		LIMIT %s
	""", (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, limit))
	airports = cur.fetchall()
	cur.close()
	conn.close()
	return airports

def get_random_target_airports(exclude_ident=None, count=5):
	conn = get_connection()
	cur = conn.cursor(dictionary=True)

	exclude_clause = "AND ident != %s" if exclude_ident else ""
	params = [exclude_ident] if exclude_ident else []

	cur.execute(f"""
		SELECT ident, name, municipality, iso_country
		FROM airport
		WHERE type IN ('large_airport', 'medium_airport')
		{exclude_clause}
		ORDER BY RAND()
		LIMIT %s
	""", params + [count])

	airports = cur.fetchall()
	cur.close()
	conn.close()
	return airports

def list_reachable_airports(current_ident, player_co2):
	conn = get_connection()
	cur = conn.cursor(dictionary=True)
	cur.execute("SELECT ident, name, municipality, iso_country, latitude_deg, longitude_deg FROM airport")
	airports = cur.fetchall()
	cur.close()
	conn.close()

	current = get_airport(current_ident)
	results = []
	for airport in airports:
		if airport["ident"] == current_ident:
			continue
		dist = haversine(current["latitude_deg"], current["longitude_deg"], airport["latitude_deg"], airport["longitude_deg"])
		co2 = co2_cost_km(dist)

		if co2 <= player_co2:
			results.append({
			"ident": airport["ident"],
			"name": airport["name"],
			"city": airport["municipality"],
			"country": airport["iso_country"],
			"distance_km": round(dist, 1),
			"co2_cost": round(co2, 1)
			})
	return results

def start_new_game(screen_name: str, start_airport_ident: str):
	global CURRENT_GAME

	target_airports = get_random_target_airports(exclude_ident=start_airport_ident, count=5)
	CURRENT_GAME = GameState(
		screen_name=screen_name,
		start_airport_ident=start_airport_ident,
		co2_budget=SETTINGS["initial_co2_budget"],
		target_airports=target_airports,
	)

	start_airport = get_airport(start_airport_ident)
	return {
		"success": True,
		"message": f"Game started at {start_airport['name']} ({start_airport['municipality']})",
		"start_airport": start_airport,
		"target_airports": [airport.copy() for airport in CURRENT_GAME.target_airports],
		"co2_budget": SETTINGS["initial_co2_budget"],
	}

def travel(destination_ident, target_airports=None):
	global CURRENT_GAME

	if CURRENT_GAME is None:
		return {
			"success": False,
			"message": "No active game. Start a new game first.",
			"remaining_budget": None,
			"visited_target": False,
			"remaining_targets": [],
			"targets_completed": 0,
		}

	if target_airports is not None:
		CURRENT_GAME.target_airports = [airport.copy() for airport in target_airports]

	origin = get_airport(CURRENT_GAME.location)
	dest = get_airport(destination_ident)
	dist = haversine(origin["latitude_deg"], origin["longitude_deg"], dest["latitude_deg"], dest["longitude_deg"])
	co2 = co2_cost_km(dist)

	visited_target = CURRENT_GAME.record_travel(destination_ident, co2)
	remaining_targets = [airport.copy() for airport in CURRENT_GAME.remaining_targets]

	message = f"Flew from {origin['municipality']} to {dest['municipality']} consuming {round(co2, 1)} kg CO2."
	if visited_target:
		targets_left = len(remaining_targets)
		message += f" Target airport visited! {targets_left} targets remaining."

	return {
		"success": True,
		"message": message,
		"remaining_budget": round(CURRENT_GAME.remaining_budget, 1),
		"visited_target": visited_target,
		"remaining_targets": remaining_targets,
		"targets_completed": CURRENT_GAME.targets_completed,
	}

def get_game_state():
	if CURRENT_GAME is None:
		return None

	current_airport = get_airport(CURRENT_GAME.location)

	return {
		"screen_name": CURRENT_GAME.screen_name,
		"current_airport": current_airport,
		"co2_budget": CURRENT_GAME.co2_budget,
		"co2_consumed": CURRENT_GAME.co2_consumed,
		"remaining_budget": CURRENT_GAME.remaining_budget,
		"location": CURRENT_GAME.location,
		"target_airports": [airport.copy() for airport in CURRENT_GAME.target_airports],
		"remaining_targets": [airport.copy() for airport in CURRENT_GAME.remaining_targets],
		"targets_completed": CURRENT_GAME.targets_completed,
	}

def get_settings():
	return SETTINGS.copy()

def update_settings(new_settings):
	global SETTINGS
	updated = {}

	for key, value in new_settings.items():
		if key in SETTINGS:
			SETTINGS[key] = value
			updated[key] = value
		else:
			print(f"Warning: Unknown setting '{key}' ignored")

	return {
		"success": True,
		"message": f"Updated {len(updated)} setting(s)",
		"updated_settings": updated,
		"current_settings": SETTINGS.copy()
	}

if __name__ == "__main__":
	game_info = start_new_game("TestPlayer", "EFHK")
	targets = game_info['target_airports']
	print(len(targets))
	for i, target in enumerate(targets, 1):
		print(f"  {i}. {target['ident']} - {target['name']}")

	if targets:
		target_to_visit = targets[0]
		print(f"{target_to_visit['ident']} - {target_to_visit['name']}")

		result = travel(target_to_visit['ident'], targets)
		print(result['message'])
		print(result['visited_target'])
		print(result['targets_completed'])
		print(len(result['remaining_targets']))
