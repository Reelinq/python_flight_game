import mysql.connector
import math
from mysql.connector import Error

SETTINGS = {
	"initial_co2_budget": 2000,
	"co2_per_100km": 20
}

def get_connection():
	return mysql.connector.connect(
	host="localhost",
	user="root",
	password="",
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
	target_airports = get_random_target_airports(exclude_ident=start_airport_ident, count=5)

	conn = get_connection()
	cur = conn.cursor()
	cur.execute("DELETE FROM game")
	cur.execute(
		"INSERT INTO game (co2_consumed, co2_budget, screen_name, location) VALUES (%s,%s,%s,%s)",
		(0, SETTINGS["initial_co2_budget"], screen_name, start_airport_ident)
	)
	conn.commit()
	cur.close()
	conn.close()

	start_airport = get_airport(start_airport_ident)
	return {
		"success": True,
		"message": f"Game started at {start_airport['name']} ({start_airport['municipality']})",
		"start_airport": start_airport,
		"target_airports": target_airports,
		"co2_budget": SETTINGS["initial_co2_budget"]
	}

def travel(destination_ident, target_airports=None):
	conn = get_connection()
	cur = conn.cursor(dictionary=True)

	cur.execute("SELECT co2_consumed, co2_budget, location FROM game LIMIT 1")
	game = cur.fetchone()

	origin = get_airport(game["location"])
	dest = get_airport(destination_ident)
	dist = haversine(origin["latitude_deg"], origin["longitude_deg"], dest["latitude_deg"], dest["longitude_deg"])
	co2 = co2_cost_km(dist)

	new_consumed = game["co2_consumed"] + co2

	cur.execute("UPDATE game SET co2_consumed=%s, location=%s", (new_consumed, destination_ident))
	conn.commit()
	cur.close()
	conn.close()

	visited_target = False
	remaining_targets = target_airports.copy() if target_airports else []

	if target_airports:
		for i, airport in enumerate(target_airports):
			if airport['ident'] == destination_ident:
				visited_target = True
				remaining_targets.pop(i)
				break

	message = f"Flew from {origin['municipality']} to {dest['municipality']} consuming {round(co2,1)} kg CO₂."
	if visited_target:
		targets_left = len(remaining_targets)
		message += f" Target airport visited! {targets_left} targets remaining."

	return {
		"success": True,
		"message": message,
		"remaining_budget": round(game["co2_budget"] - new_consumed, 1),
		"visited_target": visited_target,
		"remaining_targets": remaining_targets,
		"targets_completed": len(target_airports) - len(remaining_targets) if target_airports else 0
	}

def get_game_state():
	conn = get_connection()
	cur = conn.cursor(dictionary=True)
	cur.execute("SELECT * FROM game LIMIT 1")
	game = cur.fetchone()
	cur.close()
	conn.close()

	if not game:
		return None

	current_airport = get_airport(game["location"])

	remaining_budget = game["co2_budget"] - game["co2_consumed"]

	return {
		"screen_name": game["screen_name"],
		"current_airport": current_airport,
		"co2_budget": game["co2_budget"],
		"co2_consumed": game["co2_consumed"],
		"remaining_budget": remaining_budget,
		"location": game["location"]
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
