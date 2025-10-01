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

def test_get_airport():
	airport = get_airport("EFHK")

	assert airport is not None
	assert airport["ident"] == "EFHK"
	assert airport["municipality"] == "Helsinki"
	assert airport["iso_country"] == "FI"
	assert "name" in airport

	print("✅ Airport test passed!")

if __name__ == "__main__":
	test_get_airport()
