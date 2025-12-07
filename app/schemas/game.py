from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.schemas.airport import AirportMinimal

class StartGameIn(BaseModel):
    screen_name: str
    start_airport_ident: str

class TravelIn(BaseModel):
    destination_ident: str

class GameStateOut(BaseModel):
    id: int
    screen_name: str
    location_ident: str
    co2_budget: float
    co2_consumed: float
    remaining_budget: float = Field(..., alias="remainingBudget")
    target_airports: List[AirportMinimal]
    remaining_targets: List[AirportMinimal]
    targets_completed: int
    current_airport: AirportMinimal

class TravelResultOut(BaseModel):
    success: bool
    message: str
    remaining_budget: float
    visited_target: bool
    remaining_targets: List[AirportMinimal]
    targets_completed: int
