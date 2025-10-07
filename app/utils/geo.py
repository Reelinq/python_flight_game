import math

EARTH_RADIUS_KM = 6371.0

def haversine(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> float:
    s_lat = math.radians(start_lat)
    e_lat = math.radians(end_lat)
    d_lat = math.radians(end_lat - start_lat)
    d_lon = math.radians(end_lon - start_lon)

    a = (math.sin(d_lat/2)**2 +
         math.cos(s_lat)*math.cos(e_lat)*math.sin(d_lon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return EARTH_RADIUS_KM * c
