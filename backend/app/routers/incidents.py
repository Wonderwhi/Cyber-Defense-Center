from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
)

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)

# Incident management routes for create, read, update, and delete operations.

# Database Dependency
# Provides a single SQLAlchemy session per request and closes it afterward.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=IncidentResponse)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    reporter = db.query(User).filter(User.id == incident.reported_by).first()
    if not reporter:
        raise HTTPException(status_code=400, detail="reported_by must reference an existing user")

    new_incident = Incident(
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status="Open",
        reported_by=incident.reported_by
    )

    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    return new_incident


@router.get("/", response_model=list[IncidentResponse])
def get_incidents(
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
):
    # Start with the full incidents query, then layer on filters and sorting.
    query = db.query(Incident)

    # Search title and description with a case-insensitive partial match.
    if search:
        query = query.filter(
            (Incident.title.ilike(f"%{search}%")) |
            (Incident.description.ilike(f"%{search}%"))
        )

    # Allow only a small, predictable set of sort fields.
    if sort_by == "severity":
        sort_column = Incident.severity
    elif sort_by == "title":
        sort_column = Incident.title
    else:
        sort_column = Incident.created_at

    # Default to newest-first unless the caller explicitly asks for ascending order.
    if order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    return query.all()


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    reporter = db.query(User).filter(User.id == incident_update.reported_by).first()
    if not reporter:
        raise HTTPException(status_code=400, detail="reported_by must reference an existing user")

    incident.title = incident_update.title
    incident.description = incident_update.description
    incident.severity = incident_update.severity
    incident.status = incident_update.status
    incident.reported_by = incident_update.reported_by

    db.commit()
    db.refresh(incident)

    return incident


@router.delete("/{incident_id}")
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    db.delete(incident)
    db.commit()

    return {"detail": "Incident deleted successfully"}