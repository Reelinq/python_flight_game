from app.core.config import settings

def get_settings():
    return {
        "initial_co2_budget": settings.initial_co2_budget,
        "co2_per_100km": settings.co2_per_100km
    }

def update_settings(data: dict):
    if "initial_co2_budget" in data and data["initial_co2_budget"] is not None:
        settings.initial_co2_budget = float(data["initial_co2_budget"])
    if "co2_per_100km" in data and data["co2_per_100km"] is not None:
        settings.co2_per_100km = float(data["co2_per_100km"])
    return get_settings()
