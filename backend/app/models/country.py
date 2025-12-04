from sqlalchemy import Column, String
from app.core.db import Base

class Country(Base):
    __tablename__ = "country"

    iso_country = Column(String(40), primary_key=True)
    name = Column(String(40))
    continent = Column(String(40))
    wikipedia_link = Column(String(40))
    keywords = Column(String(40))
