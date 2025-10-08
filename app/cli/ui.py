from __future__ import annotations
from typing import Optional, List
import random
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

    remaining_idents = {t.ident for t in state.remaining_targets}

    for t in state.target_airports:
        city = t.municipality or "-"
        if t.ident in remaining_idents:
            print(f"  ⏳ {t.ident} ({t.name or '-'}, {city}) - Not visited")
        else:
            print(f"  ✅ {t.ident} ({t.name or '-'}, {city}) - VISITED")

    print(f"CO2 Budget: {state.co2_budget} | Remaining: {state.remaining_budget}")
    print(f"Progress: {state.targets_completed}/{len(state.target_airports)} targets completed\n")

def show_targets_with_costs(client: ApiClient, game_id: int, state: GameState) -> None:
    print("\nTarget airports:")

    try:
        reachable_data = client.reachable(game_id)
        cost_lookup = {airport['ident']: airport['co2_cost'] for airport in reachable_data}
    except ApiError:
        cost_lookup = {}

    remaining_idents = {t.ident for t in state.remaining_targets}

    for t in state.target_airports:
        city = t.municipality or "-"
        co2_cost = cost_lookup.get(t.ident, "?")
        cost_str = f" (CO2: {round(co2_cost)} kg)" if co2_cost != "?" else " (CO2: N/A)"

        if t.ident in remaining_idents:
            print(f"  ⏳ {t.ident} ({t.name or '-'}, {city}){cost_str} - Not visited")
        else:
            print(f"  ✅ {t.ident} ({t.name or '-'}, {city}) - VISITED")

    print(f"CO2 Budget: {state.co2_budget} | Remaining: {state.remaining_budget}")
    print(f"Progress: {state.targets_completed}/{len(state.target_airports)} targets completed\n")

def game_loop(client: ApiClient, state: GameState) -> None:
    game_id = state.id
    show_targets_with_costs(client, game_id, state)

    while True:
        print("1. Show state")
        print("2. Travel")
        print("3. Exit to main menu")
        choice = prompt_int("Choose: ", 1, 3)

        if choice == 1:
            try:
                state = client.get_state(game_id)
                print(f"\nAt: {state.location_ident} | Remaining: {state.remaining_budget} | Targets done: {state.targets_completed}")
                show_targets_with_costs(client, game_id, state)

                # Check if game is over only when showing state
                try:
                    over = client.is_over(game_id)
                    if over:
                        current_state = client.get_state(game_id)
                        if current_state.targets_completed == len(current_state.target_airports):
                            print("\n🎉 CONGRATULATIONS! 🎉")
                            print("You successfully visited all target airports!")
                            print(f"Final stats: {current_state.targets_completed}/{len(current_state.target_airports)} targets completed")
                            print(f"CO2 used: {round(current_state.co2_budget - current_state.remaining_budget)}/{current_state.co2_budget} kg")
                            print("You are a master pilot! ✈️\n")
                        else:
                            print("\n💨 GAME OVER 💨")
                            print("You cannot reach any remaining targets with your current CO2 budget.")
                            print(f"Final stats: {current_state.targets_completed}/{len(current_state.target_airports)} targets completed")
                            print(f"CO2 remaining: {current_state.remaining_budget}/{current_state.co2_budget} kg")
                            print("Better luck next time! 🌍\n")
                        input("Press Enter to return to main menu...")
                        break
                except ApiError:
                    pass

            except ApiError as e:
                print(f"API error: {e}")

        elif choice == 2:
            dest = input("Destination ident: ").strip().upper()
            if not dest:
                print("Type an ICAO/IATA ident.")
                continue
            try:
                current_state = client.get_state(game_id)
            except ApiError:
                pass

            try:
                result = client.travel(game_id, dest)
                print(f"\n{result.message}")
                print(f"Remaining budget: {result.remaining_budget}, Targets done: {result.targets_completed}\n")
            except ApiError as e:
                try:
                    over = client.is_over(game_id)
                    if over:
                        current_state = client.get_state(game_id)
                        if current_state.targets_completed == len(current_state.target_airports):
                            print("\n🎉 CONGRATULATIONS! 🎉")
                            print("You successfully visited all target airports!")
                            print(f"Final stats: {current_state.targets_completed}/{len(current_state.target_airports)} targets completed")
                            print(f"CO2 used: {round(current_state.co2_budget - current_state.remaining_budget)}/{current_state.co2_budget} kg")
                            print("You are a master pilot! ✈️\n")
                        else:
                            print("\n💨 GAME OVER 💨")
                            print("You cannot reach any remaining targets with your current CO2 budget.")
                            print(f"Final stats: {current_state.targets_completed}/{len(current_state.target_airports)} targets completed")
                            print("Better luck next time! 🌍\n")
                        input("Press Enter to return to main menu...")
                        break
                    else:
                        print(f"Travel failed: {e}")
                except ApiError:
                    print(f"Travel failed: {e}")

        elif choice == 3:
            break

def main_menu(client: ApiClient) -> None:
    while True:
        print("\n=== Flight Game ===")
        print("1. Start Game")
        print("2. Settings")
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
            settings_menu(client)

        elif choice == 3:
            break

def settings_menu(client: ApiClient) -> None:
    """Handles the settings menu for randomizing the next game's CO₂ budget."""
    try:
        s = client.get_settings()
        print(f"\nCurrent settings -> initial_co2_budget={s.initial_co2_budget}, co2_per_100km={s.co2_per_100km}")
    except ApiError as e:
        print(f"API error fetching settings: {e}")

    setting_choice = input(
        "Would you like random or manual settings?\n"
        "(1) Set manually (budget and CO₂ rate)\n"
        "(2) Randomize next game's CO₂ budget\n"
        "(3) Return to main menu\n"
        "Your choice: "
    ).strip()

    if setting_choice == "1":
        # Manual configuration: prompt for budget and CO₂ consumption
        def _prompt_float(msg: str, min_val: float = 0.0) -> float:
            while True:
                raw = input(msg).strip()
                try:
                    val = float(raw)
                    if val < min_val:
                        raise ValueError()
                    return val
                except ValueError:
                    print(f"Enter a number >= {min_val}.")

        budget = _prompt_float("Enter initial CO₂ budget in kg (e.g., 2000): ", 0.0)

        print("Choose CO₂ consumption unit:")
        print("  1) per 100 km (e.g., 20)")
        print("  2) per km (e.g., 0.2)")
        unit = ""
        while unit not in ("1", "2"):
            unit = input("Unit (1/2): ").strip()

        if unit == "1":
            rate_val = _prompt_float("Enter CO₂ per 100 km (kg): ", 0.0)
            rate_per_100km = rate_val
        else:
            rate_val = _prompt_float("Enter CO₂ per km (kg): ", 0.0)
            rate_per_100km = rate_val * 100.0

        try:
            updated = client.update_settings(
                initial_co2_budget=budget,
                co2_per_100km=rate_per_100km,
            )
            print(
                f"\n✅ Updated settings: initial_co2_budget={updated.initial_co2_budget} kg, "
                f"co2_per_100km={updated.co2_per_100km} kg."
            )
        except ApiError as e:
            print(f"⚠️ Couldn't update settings — {e}")
        return

    if setting_choice == "2":
        # Randomize a new initial CO₂ budget and update via new settings route
        new_budget = float(random.randint(1000, 67000))
        try:
            updated = client.update_settings(initial_co2_budget=new_budget)
            print(f"\n✅ Next game will use a random CO₂ budget: {updated.initial_co2_budget} kg.")
        except ApiError as e:
            print(f"⚠️ Couldn't update settings — {e}")
        return

    if setting_choice == "3":
        print("Returning to main menu.")
        return

    print("Invalid choice. Please try again.")
