from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import TypedDict

from app.database.database import get_db
from app.models.incident import Incident

router = APIRouter()


class PriorityStats(TypedDict):
    """The number of incidents at each priority level."""

    high: int
    medium: int
    low: int


class CategoryStats(TypedDict):
    """The number of incidents in each category."""

    phishing: int
    malware: int
    ransomware: int


class DashboardStatsResponse(TypedDict):
    """The data shown in the dashboard summary and charts."""

    total_incidents: int
    open_incidents: int
    closed_incidents: int
    critical_incidents: int
    priority: PriorityStats
    categories: CategoryStats


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)) -> DashboardStatsResponse:
    """Get the incident counts needed by the dashboard."""

    # These counts appear in the summary cards at the top of the dashboard.
    total = int(db.query(Incident).count())

    open_incidents = (
        db.query(Incident)
        .filter(Incident.status == "Open")
        .count()
    )

    closed_incidents = (
        db.query(Incident)
        .filter(Incident.status == "Closed")
        .count()
    )

    critical_incidents = (
        db.query(Incident)
        .filter(Incident.severity == "Critical")
        .count()
    )

    # Use the same capitalization as the values stored in the database.
    # The dashboard uses these numbers to show the priority breakdown.
    high_priority = (
        db.query(Incident)
        .filter(Incident.priority == "High")
        .count()
    )

    medium_priority = (
        db.query(Incident)
        .filter(Incident.priority == "Medium")
        .count()
    )

    low_priority = (
        db.query(Incident)
        .filter(Incident.priority == "Low")
        .count()
    )

    # These numbers populate the category chart. A spelling or capitalization
    # change here would make a category appear empty even when it has records.
    phishing = (
        db.query(Incident)
        .filter(Incident.category == "Phishing")
        .count()
    )

    malware = (
        db.query(Incident)
        .filter(Incident.category == "Malware")
        .count()
    )

    ransomware = (
        db.query(Incident)
        .filter(Incident.category == "Ransomware")
        .count()
    )

    return {
        "total_incidents": total,
        "open_incidents": int(open_incidents),
        "closed_incidents": int(closed_incidents),
        "critical_incidents": int(critical_incidents),
        "priority": {
            "high": int(high_priority),
            "medium": int(medium_priority),
            "low": int(low_priority),
        },
        "categories": {
            "phishing": int(phishing),
            "malware": int(malware),
            "ransomware": int(ransomware),
        },
    }