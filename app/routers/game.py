from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.game import StartGameIn, TravelIn, GameStateOut, TravelResultOut
from app.schemas.airport import AirportMinimal
from app.services import game_service

router = APIRouter(prefix="/game", tags=["game"])

@router.post("/start", response_model=GameStateOut)
def start_game(body: StartGameIn, db: Session = Depends(get_db)):
    try:
        g = game_service.start_game(db, body.screen_name, body.start_airport_ident)
        state = game_service.get_state(db, g.id)
        return GameStateOut(
            id=state["id"],
            screen_name=state["screen_name"],
            location_ident=state["location_ident"],
            co2_budget=state["co2_budget"],
            co2_consumed=state["co2_consumed"],
            remainingBudget=state["remainingBudget"],
            target_airports=[AirportMinimal(**x) for x in state["target_airports"]],
            remaining_targets=[AirportMinimal(**x) for x in state["remaining_targets"]],
            targets_completed=state["targets_completed"],
            current_airport=AirportMinimal(**state["current_airport"]),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{game_id}/state", response_model=GameStateOut)
def get_state(game_id: int, db: Session = Depends(get_db)):
    try:
        state = game_service.get_state(db, game_id)
        return GameStateOut(
            id=state["id"],
            screen_name=state["screen_name"],
            location_ident=state["location_ident"],
            co2_budget=state["co2_budget"],
            co2_consumed=state["co2_consumed"],
            remainingBudget=state["remainingBudget"],
            target_airports=[AirportMinimal(**x) for x in state["target_airports"]],
            remaining_targets=[AirportMinimal(**x) for x in state["remaining_targets"]],
            targets_completed=state["targets_completed"],
            current_airport=AirportMinimal(**state["current_airport"]),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{game_id}/travel", response_model=TravelResultOut)
def travel(game_id: int, body: TravelIn, db: Session = Depends(get_db)):
    try:
        result = game_service.travel(db, game_id, body.destination_ident)
        return TravelResultOut(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{game_id}/reachable")
def reachable(game_id: int, db: Session = Depends(get_db)):
    try:
        return game_service.list_reachable(db, game_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{game_id}/over")
def game_over(game_id: int, db: Session = Depends(get_db)):
    try:
        return { "game_over": game_service.is_game_over(db, game_id) }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
