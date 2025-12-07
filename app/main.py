from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.db import engine
from app.models.game import Game
from app.routers import airports, game, settings
from app.web import routes as web_routes

Game.__table__.create(bind=engine, checkfirst=True)

app = FastAPI(title="Flight Game API", version="1.0.0")

app.include_router(airports.router)
app.include_router(game.router)
app.include_router(settings.router)
app.include_router(web_routes.router)
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

@app.get("/")
def health():
    return {"ok": True}
