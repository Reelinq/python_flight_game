from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class AirportMinimal(BaseModel):
    ident: str
    name: Optional[str] = None
    municipality: Optional[str] = None
    iso_country: Optional[str] = None
    latitude_deg: Optional[float] = None
    longitude_deg: Optional[float] = None

class GameState(BaseModel):
    id: int
    screen_name: str
    location_ident: str
    co2_budget: float
    co2_consumed: float
    remaining_budget: float = Field(alias="remainingBudget")
    target_airports: List[AirportMinimal]
    remaining_targets: List[AirportMinimal]
    targets_completed: int
    current_airport: AirportMinimal | None = None

class TravelResult(BaseModel):
    success: bool
    message: str
    remaining_budget: float
    visited_target: bool
    remaining_targets: List[AirportMinimal]
    targets_completed: int

class SettingsOut(BaseModel):
    initial_co2_budget: float
    co2_per_100km: float

class SettingsIn(BaseModel):
    initial_co2_budget: float | None = None
    co2_per_100km: float | None = None
