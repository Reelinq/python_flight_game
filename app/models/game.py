from sqlalchemy import Column, Integer, String, Float, JSON

from app.core.db import Base

class Game(Base):
    __tablename__ = "game_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    screen_name = Column(String(50), index=True)
    location_ident = Column(String(40))
    co2_budget = Column(Float, default=0)
    co2_consumed = Column(Float, default=0)
    target_airports = Column(JSON, nullable=False)
    visited_idents = Column(JSON, nullable=False, default=[])
