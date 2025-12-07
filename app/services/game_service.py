from sqlalchemy.orm import Session
from typing import List, Dict
from app.repositories import airport_repo, game_repo
from app.utils.geo import haversine
from app.utils.co2 import co2_cost_km
from app.core.config import settings
from app.models.game import Game

def _remaining_targets(game: Game) -> List[Dict]:
    visited = set(game.visited_idents or [])
    return [a for a in (game.target_airports or []) if a["ident"] not in visited]

def _targets_completed(game: Game) -> int:
    return len(set(game.visited_idents or []))

def start_game(db: Session, screen_name: str, start_ident: str) -> Game:
    if not airport_repo.get_by_ident(db, start_ident):
        raise ValueError("Invalid start airport ident")

    targets = airport_repo.random_targets(db, exclude_ident=start_ident, count=5)
    g = game_repo.create(
        db,
        screen_name=screen_name,
        location_ident=start_ident,
        co2_budget=float(settings.initial_co2_budget),
        co2_consumed=0.0,
        target_airports=targets,
        visited_idents=[]
    )
    return g

def get_state(db: Session, game_id: int) -> dict:
    g = game_repo.get(db, game_id)
    if not g:
        raise ValueError("Game not found")

    current = airport_repo.get_by_ident(db, g.location_ident)
    if not current:
        raise ValueError("Current airport not found")

    remaining = _remaining_targets(g)

    return {
        "id": g.id,
        "screen_name": g.screen_name,
        "location_ident": g.location_ident,
        "co2_budget": g.co2_budget,
        "co2_consumed": g.co2_consumed,
        "remainingBudget": g.co2_budget - g.co2_consumed,
        "target_airports": g.target_airports,
        "remaining_targets": remaining,
        "targets_completed": _targets_completed(g),
        "current_airport": {
            "ident": current.ident,
            "name": current.name,
            "municipality": current.municipality,
            "iso_country": current.iso_country,
            "latitude_deg": current.latitude_deg,
            "longitude_deg": current.longitude_deg,
        }
    }

def travel(db: Session, game_id: int, destination_ident: str) -> dict:
    g = game_repo.get(db, game_id)
    if not g:
        raise ValueError("Game not found")

    origin = airport_repo.get_by_ident(db, g.location_ident)
    dest = airport_repo.get_by_ident(db, destination_ident)
    if not origin or not dest:
        raise ValueError("Origin or destination not found")

    dist = haversine(origin.latitude_deg, origin.longitude_deg, dest.latitude_deg, dest.longitude_deg)
    co2 = co2_cost_km(dist, settings.co2_per_100km)

    # Prevent overspending CO2 budget
    remaining_before = g.co2_budget - g.co2_consumed
    if co2 > remaining_before:
        raise ValueError("Insufficient CO2 budget for this flight")

    g.co2_consumed = float(g.co2_consumed + co2)
    g.location_ident = destination_ident

    visited = set(g.visited_idents or [])
    was_target = False
    for a in (g.target_airports or []):
        if a["ident"] == destination_ident and destination_ident not in visited:
            visited.add(destination_ident)
            was_target = True
            break
    g.visited_idents = list(visited)

    game_repo.save(db, g)

    remaining = _remaining_targets(g)
    msg = f"Flew from {origin.municipality} to {dest.municipality} consuming {round(co2,1)} kg CO2."
    if was_target:
        msg += f" Target airport visited! {len(remaining)} targets remaining."

    return {
        "success": True,
        "message": msg,
        "remaining_budget": round(g.co2_budget - g.co2_consumed, 1),
        "visited_target": was_target,
        "remaining_targets": remaining,
        "targets_completed": _targets_completed(g),
    }

def list_reachable(db: Session, game_id: int):
    g = game_repo.get(db, game_id)
    if not g:
        raise ValueError("Game not found")

    origin = airport_repo.get_by_ident(db, g.location_ident)
    if not origin:
        raise ValueError("Origin not found")

    results = []

    from sqlalchemy import select
    from app.models.airport import Airport
    airports = db.execute(select(Airport)).scalars().all()

    remaining_budget = g.co2_budget - g.co2_consumed
    for a in airports:
        if a.ident == origin.ident:
            continue
        dist = haversine(origin.latitude_deg, origin.longitude_deg, a.latitude_deg, a.longitude_deg)
        co2 = co2_cost_km(dist, settings.co2_per_100km)
        if co2 <= remaining_budget:
            results.append({
                "ident": a.ident,
                "name": a.name,
                "city": a.municipality,
                "country": a.iso_country,
                "distance_km": round(dist, 1),
                "co2_cost": round(co2, 1),
                "latitude_deg": a.latitude_deg,
                "longitude_deg": a.longitude_deg,
            })
    return results

def is_game_over(db: Session, game_id: int) -> bool:
    g = game_repo.get(db, game_id)
    if not g:
        raise ValueError("Game not found")

    if len(_remaining_targets(g)) == 0:
        return True

    origin = airport_repo.get_by_ident(db, g.location_ident)
    if not origin:
        return False

    remaining_budget = g.co2_budget - g.co2_consumed
    if remaining_budget <= 0:
        return True

    for t in _remaining_targets(g):
        dest = airport_repo.get_by_ident(db, t["ident"])
        if not dest:
            continue
        dist = haversine(origin.latitude_deg, origin.longitude_deg, dest.latitude_deg, dest.longitude_deg)
        co2 = co2_cost_km(dist, settings.co2_per_100km)
        if co2 <= remaining_budget:
            return False
    return True
