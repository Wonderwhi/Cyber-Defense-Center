from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate


def create_incident(db: Session, incident: IncidentCreate):
    db_incident = Incident(**incident.model_dump())

    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return db_incident


def get_incident(db: Session, incident_id: int):
    return db.query(Incident).filter(Incident.id == incident_id).first()


def get_all_incidents(db: Session):
    return db.query(Incident).all()

def update_incident(db: Session, incident_id: int, incident: IncidentUpdate):
    db_incident = get_incident(db, incident_id)

    if not db_incident:
        return None

    update_data = incident.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_incident, key, value)

    db.commit()
    db.refresh(db_incident)

    return db_incident

def delete_incident(db: Session, incident_id: int):
    db_incident = get_incident(db, incident_id)

    if not db_incident:
        return None

    db.delete(db_incident)
    db.commit()

    return db_incident