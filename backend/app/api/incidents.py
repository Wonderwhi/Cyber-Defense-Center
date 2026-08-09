from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
)

from app.crud.incident import (
    create_incident,
    get_incident,
    get_all_incidents,
    update_incident,
    delete_incident,
)

router = APIRouter()


@router.post("/", response_model=IncidentResponse)
def create_new_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
):
    # Keep the route thin and let the CRUD layer handle the database write.
    return create_incident(db, incident)


@router.get("/", response_model=list[IncidentResponse])
def read_incidents(db: Session = Depends(get_db)):
    return get_all_incidents(db)


@router.get("/{incident_id}", response_model=IncidentResponse)
def read_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = get_incident(db, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
def update_existing_incident(
    incident_id: int,
    incident: IncidentUpdate,
    db: Session = Depends(get_db),
):
    updated = update_incident(
        db,
        incident_id,
        incident,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return updated


@router.delete("/{incident_id}")
def delete_existing_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_incident(
        db,
        incident_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return {
        "message": "Incident deleted successfully"
    }
