from pydantic import BaseModel

class SettingsOut(BaseModel):
    initial_co2_budget: float
    co2_per_100km: float

class SettingsIn(BaseModel):
    initial_co2_budget: float | None = None
    co2_per_100km: float | None = None
