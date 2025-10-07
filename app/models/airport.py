from sqlalchemy import Column, Integer, String, Float
from app.core.db import Base

class Airport(Base):
    __tablename__ = "airport"

    id = Column(Integer, primary_key=True)
    ident = Column(String(40), index=True, nullable=False)

    type = Column(String(40))
    name = Column(String(40))
    latitude_deg = Column(Float)
    longitude_deg = Column(Float)
    elevation_ft = Column(Integer)
    continent = Column(String(40))
    iso_country = Column(String(40))
    iso_region = Column(String(40))
    municipality = Column(String(40))
    scheduled_service = Column(String(40))
    gps_code = Column(String(40))
    iata_code = Column(String(40))
    local_code = Column(String(40))
    home_link = Column(String(40))
    wikipedia_link = Column(String(40))
    keywords = Column(String(40))
