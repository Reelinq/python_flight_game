from __future__ import annotations
import httpx
from typing import Any, Dict, List, Optional
from .types import AirportMinimal, GameState, TravelResult, SettingsOut, SettingsIn

DEFAULT_BASE_URL = "http://127.0.0.1:8000"

class ApiError(RuntimeError):
    pass

class ApiClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._http = httpx.Client(base_url=self.base_url, timeout=timeout)

    def close(self) -> None:
        self._http.close()

    def search_airports(self, q: str, limit: int = 5) -> List[AirportMinimal]:
        r = self._http.get("/airports/search", params={"q": q, "limit": limit})
        self._raise(r)
        return [AirportMinimal.model_validate(a) for a in r.json()]

    def get_airport(self, ident: str) -> AirportMinimal:
        r = self._http.get(f"/airports/{ident}")
        self._raise(r)
        return AirportMinimal.model_validate(r.json())

    def start_game(self, screen_name: str, start_airport_ident: str) -> GameState:
        payload = {"screen_name": screen_name, "start_airport_ident": start_airport_ident}
        r = self._http.post("/game/start", json=payload)
        self._raise(r)
        return GameState.model_validate(r.json())

    def get_state(self, game_id: int) -> GameState:
        r = self._http.get(f"/game/{game_id}/state")
        self._raise(r)
        return GameState.model_validate(r.json())

    def travel(self, game_id: int, destination_ident: str) -> TravelResult:
        r = self._http.post(f"/game/{game_id}/travel", json={"destination_ident": destination_ident})
        self._raise(r)
        return TravelResult.model_validate(r.json())

    def reachable(self, game_id: int) -> List[Dict[str, Any]]:
        r = self._http.get(f"/game/{game_id}/reachable")
        self._raise(r)
        return r.json()

    def is_over(self, game_id: int) -> bool:
        r = self._http.get(f"/game/{game_id}/over")
        self._raise(r)
        return bool(r.json().get("game_over"))

    def get_settings(self) -> SettingsOut:
        r = self._http.get("/settings")
        self._raise(r)
        return SettingsOut.model_validate(r.json())

    def update_settings(self, **kwargs) -> SettingsOut:
        r = self._http.put("/settings", json=SettingsIn(**kwargs).model_dump(exclude_none=True))
        self._raise(r)
        return SettingsOut.model_validate(r.json())

    @staticmethod
    def _raise(r: httpx.Response) -> None:
        if r.status_code >= 400:
            detail = None
            try:
                detail = r.json().get("detail")
            except Exception:
                pass
            raise ApiError(detail or f"HTTP {r.status_code}: {r.text}")
