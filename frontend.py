import backend

def main_menu():
	while True:
		print("1. Start Game")
		print("2. Settings")
		print("3. Exit")

		choice = int(input("Choose option: "))

		if choice == 1:
			start_game()
		elif choice == 2:
			print("Settings - TODO")
		elif choice == 3:
			break

def start_game():
	screen_name = input("Enter your name: ").strip()

	while True:
		search_term = input("Search for starting airport: ").strip()
		airports = backend.search_airports(search_term, limit=5)

		if not airports:
			print("No airports found! Try again.")
			continue

		print("Found airports:")
		for i, airport in enumerate(airports, 1):
			print(f"{i}. {airport['ident']} - {airport['name']} ({airport['municipality']})")
		print("0. Search again")

		try:
			choice = int(input("Select airport or search again (0): "))

			if choice == 0:
				continue

			choice = choice - 1
			selected_airport = airports[choice]
			break
		except (ValueError, IndexError):
			print("Invalid selection! Try again.")

	# Start the game
	result = backend.start_new_game(screen_name, selected_airport['ident'])

	if result['success']:
		print(f"Game started! {result['message']}")
		print(f"CO2 Budget: {result['co2_budget']} kg")
		print("Target airports:")
		for airport in result['target_airports']:
			print(f"  - {airport['ident']} ({airport['name']})")

		input("There should be a game logic...") #Placeholder
	else:
		print(f"Failed: {result['message']}")
		input("Press Enter to continue...")

if __name__ == "__main__":
	main_menu()
