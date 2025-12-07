from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/ui")
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
def start_page(request: Request):
    return templates.TemplateResponse("lobby/start.html", {"request": request})


@router.get("/lobby/name", response_class=HTMLResponse)
def name_page(request: Request):
    return templates.TemplateResponse("lobby/name.html", {"request": request})


@router.get("/lobby/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    return templates.TemplateResponse("lobby/settings.html", {"request": request})


@router.get("/move", response_class=HTMLResponse)
def move_page(request: Request):
    return templates.TemplateResponse("move/move.html", {"request": request})
