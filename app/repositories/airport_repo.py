from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, case
from app.models.airport import Airport

def get_by_ident(db: Session, ident: str) -> Airport | None:
    return db.execute(
        select(Airport).where(Airport.ident == ident)
    ).scalar_one_or_none()

def search(db: Session, term: str, limit: int = 10):
    like = f"%{term}%"

    base = select(
        Airport.ident,
        Airport.name,
        Airport.municipality,
        Airport.iso_country,
        Airport.type,
    ).where(
        Airport.type.in_(["large_airport", "medium_airport"])
    )

    if term:
        base = base.where(
            or_(
                Airport.name.ilike(like),
                Airport.municipality.ilike(like),
                Airport.ident.ilike(like),
            )
        ).order_by(
            case(
                (Airport.ident.ilike(like), 1),
                (Airport.name.ilike(like), 2),
                else_=3
            ),
            Airport.name
        )
    else:
        base = base.order_by(Airport.name)

    base = base.limit(limit)
    return db.execute(base).all()

def random_targets(db: Session, exclude_ident: str | None, count: int = 5):
    stmt = select(
        Airport.ident, Airport.name, Airport.municipality, Airport.iso_country
    ).where(
        Airport.type.in_(["large_airport", "medium_airport"])
    )
    if exclude_ident:
        stmt = stmt.where(Airport.ident != exclude_ident)
    stmt = stmt.order_by(func.rand()).limit(count)
    return [dict(r._mapping) for r in db.execute(stmt)]
