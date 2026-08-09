from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="Viewer")

    # Incidents this user reported
    reported_incidents = relationship(
        "Incident",
        foreign_keys="Incident.reported_by",
        back_populates="reporter",
    )

    # Incidents assigned to this user
    assigned_incidents = relationship(
        "Incident",
        foreign_keys="Incident.assigned_to",
        back_populates="assignee",
    )