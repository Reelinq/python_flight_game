def co2_cost_km(distance_km: float, co2_per_100km: float) -> float:
    return distance_km * (co2_per_100km / 100.0)
