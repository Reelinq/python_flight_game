import mysql.connector
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

if __name__ == "__main__":
	conn = get_connection()
	if conn:
		print("✅ Connected to database!")
		conn.close()
