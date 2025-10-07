from __future__ import annotations
from typing import Optional, List
from .api import ApiClient, ApiError
from .types import AirportMinimal, GameState, TravelResult

def prompt_int(msg: str, min_val: int, max_val: int) -> int:
    while True:
        try:
            v = int(input(msg))
            if v < min_val or v > max_val:
                raise ValueError()
            return v
        except ValueError:
            print(f"Enter a number between {min_val}-{max_val}.")

def pick_airport(client: ApiClient, limit: int = 5) -> AirportMinimal:
    while True:
        term = input("Search for starting airport: ").strip()
        if not term:
            print("Type something.")
            continue
        try:
            results = client.search_airports(term, limit=limit)
        except ApiError as e:
            print(f"API error: {e}")
            continue

        if not results:
            print("No airports found. Try again.")
            continue

        print("\nFound airports:")
        for i, a in enumerate(results, 1):
            city = a.municipality or "-"
            print(f"{i}. {a.ident} - {a.name or '-'} ({city})")
        print("0. Search again")

        choice = prompt_int("Select airport: ", 0, len(results))
        if choice == 0:
            continue
        return results[choice - 1]

def show_targets(state: GameState) -> None:
    print("\nTarget airports:")
    for t in state.target_airports:
        city = t.municipality or "-"
        print(f"  - {t.ident} ({t.name or '-'}, {city})")
    print(f"CO2 Budget: {state.co2_budget} | Remaining: {state.remaining_budget}\n")

def game_loop(client: ApiClient, state: GameState) -> None:
    game_id = state.id
    show_targets(state)

    while True:
        print("1. Show state")
        print("2. List reachable")
        print("3. Travel")
        print("4. Check game over")
        print("5. Exit to main menu")
        choice = prompt_int("Choose: ", 1, 5)

        if choice == 1:
            try:
                state = client.get_state(game_id)
                print(f"\nAt: {state.location_ident} | Remaining: {state.remaining_budget} | Targets done: {state.targets_completed}")
                show_targets(state)
            except ApiError as e:
                print(f"API error: {e}")

        elif choice == 2:
            try:
                data = client.reachable(game_id)
                if not data:
                    print("\nNothing reachable with current budget.")
                else:
                    print("\nReachable airports:")
                    for r in data[:25]:
                        print(f" - {r['ident']}: {r['name']} ({r['city']}), {r['distance_km']} km, {r['co2_cost']} kg")
                print()
            except ApiError as e:
                print(f"API error: {e}")

        elif choice == 3:
            dest = input("Destination ident: ").strip().upper()
            if not dest:
                print("Type an ICAO/IATA ident.")
                continue
            try:
                result = client.travel(game_id, dest)
                print(f"\n{result.message}")
                print(f"Remaining budget: {result.remaining_budget}, Targets done: {result.targets_completed}\n")
            except ApiError as e:
                print(f"API error: {e}")

        elif choice == 4:
            try:
                over = client.is_over(game_id)
                print("\nGame over!" if over else "\nYou can still continue.")
            except ApiError as e:
                print(f"API error: {e}")

        elif choice == 5:
            break

def main_menu(client: ApiClient) -> None:
    while True:
        print("\n=== Flight Game ===")
        print("1. Start Game")
        print("2. Settings (view)")
        print("3. Exit")
        choice = prompt_int("Choose: ", 1, 3)

        if choice == 1:
            screen_name = input("Enter your name: ").strip() or "Player"
            start = pick_airport(client)
            try:
                state = client.start_game(screen_name, start.ident)
                print(f"\nGame started at {start.ident} for {screen_name}.")
                game_loop(client, state)
            except ApiError as e:
                print(f"Failed to start: {e}")

        elif choice == 2:
            try:
                s = client.get_settings()
                print(f"\nSettings -> initial_co2_budget={s.initial_co2_budget}, co2_per_100km={s.co2_per_100km}\n")
            except ApiError as e:
                print(f"API error: {e}")

        elif choice == 3:
            break
