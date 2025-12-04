from fastapi import APIRouter
from app.schemas.settings import SettingsOut, SettingsIn
from app.services import settings_service

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("", response_model=SettingsOut)
def get_settings():
    s = settings_service.get_settings()
    return SettingsOut(**s)

@router.put("", response_model=SettingsOut)
def update_settings(body: SettingsIn):
    s = settings_service.update_settings(body.model_dump(exclude_unset=True))
    return SettingsOut(**s)
