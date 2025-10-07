from fastapi import FastAPI
from app.core.db import engine
from app.models.game import Game
from app.routers import airports, game, settings

Game.__table__.create(bind=engine, checkfirst=True)

app = FastAPI(title="Flight Game API", version="1.0.0")

app.include_router(airports.router)
app.include_router(game.router)
app.include_router(settings.router)

@app.get("/")
def health():
    return {"ok": True}
