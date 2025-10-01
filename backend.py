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

def test_haversine():
	assert haversine(40.7128, -74.0060, 40.7128, -74.0060) == 0.0

	ny_lat, ny_lon = 40.7128, -74.0060
	boston_lat, boston_lon = 42.3601, -71.0589
	distance = haversine(ny_lat, ny_lon, boston_lat, boston_lon)

	assert 290 < distance < 310

	print("✅ Haversine test passed!")

if __name__ == "__main__":
	test_haversine()
