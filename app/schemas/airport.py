from pydantic import BaseModel
from typing import Optional

class AirportMinimal(BaseModel):
    ident: str
    name: Optional[str] = None
    municipality: Optional[str] = None
    iso_country: Optional[str] = None

class AirportFull(AirportMinimal):
    type: Optional[str] = None
    latitude_deg: Optional[float] = None
    longitude_deg: Optional[float] = None
    elevation_ft: Optional[int] = None
    continent: Optional[str] = None
    iso_region: Optional[str] = None
    scheduled_service: Optional[str] = None
    gps_code: Optional[str] = None
    iata_code: Optional[str] = None
    local_code: Optional[str] = None
    home_link: Optional[str] = None
    wikipedia_link: Optional[str] = None
    keywords: Optional[str] = None

    class Config:
        from_attributes = True
