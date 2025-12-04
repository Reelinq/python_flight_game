from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.game import Game

def create(db: Session, **kwargs) -> Game:
    g = Game(**kwargs)
    db.add(g)
    db.commit()
    db.refresh(g)
    return g

def get(db: Session, game_id: int) -> Game | None:
    return db.get(Game, game_id)

def find_by_screen_name(db: Session, screen_name: str) -> Game | None:
    stmt = select(Game).where(Game.screen_name == screen_name).order_by(Game.id.desc()).limit(1)
    return db.execute(stmt).scalar_one_or_none()

def save(db: Session, game: Game) -> Game:
    db.add(game)
    db.commit()
    db.refresh(game)
    return game
