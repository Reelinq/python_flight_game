from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.repositories import airport_repo
from app.schemas.airport import AirportMinimal, AirportFull

router = APIRouter(prefix="/airports", tags=["airports"])

@router.get("/search", response_model=list[AirportMinimal])
def search_airports(q: str = Query(""), limit: int = Query(10, ge=1, le=300), db: Session = Depends(get_db)):
    rows = airport_repo.search(db, q, limit)
    out = []
    for r in rows:
        m = r._mapping
        out.append({
            "ident": m["ident"],
            "name": m["name"],
            "municipality": m["municipality"],
            "iso_country": m["iso_country"],
            "latitude_deg": m["latitude_deg"],
            "longitude_deg": m["longitude_deg"],
        })
    return out


@router.get("/viewport", response_model=list[AirportMinimal])
def airports_in_viewport(
    min_lat: float = Query(..., description="South latitude"),
    max_lat: float = Query(..., description="North latitude"),
    min_lon: float = Query(..., description="West longitude"),
    max_lon: float = Query(..., description="East longitude"),
    limit: int = Query(500, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    rows = airport_repo.search_in_bbox(db, min_lat, max_lat, min_lon, max_lon, limit)
    return rows

@router.get("/{ident}", response_model=AirportFull)
def get_airport(ident: str, db: Session = Depends(get_db)):
    a = airport_repo.get_by_ident(db, ident)
    if not a:
        raise HTTPException(status_code=404, detail="Airport not found")
    return a
