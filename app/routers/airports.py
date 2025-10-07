from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.repositories import airport_repo
from app.schemas.airport import AirportMinimal, AirportFull

router = APIRouter(prefix="/airports", tags=["airports"])

@router.get("/search", response_model=list[AirportMinimal])
def search_airports(q: str = Query(""), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    rows = airport_repo.search(db, q, limit)
    out = []
    for r in rows:
        m = r._mapping
        out.append({
            "ident": m["ident"],
            "name": m["name"],
            "municipality": m["municipality"],
            "iso_country": m["iso_country"],
        })
    return out

@router.get("/{ident}", response_model=AirportFull)
def get_airport(ident: str, db: Session = Depends(get_db)):
    a = airport_repo.get_by_ident(db, ident)
    if not a:
        raise HTTPException(status_code=404, detail="Airport not found")
    return a
