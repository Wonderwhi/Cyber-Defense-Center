from fastapi import FastAPI

from app.database.database import Base, engine, ensure_user_schema
from app.routers.users import router as users_router

from app.models.user import User
from app.models.incident import Incident

from app.routers.incidents import router as incidents_router

# Create all database tables that are defined in the SQLAlchemy models.
# This is a simple schema creation step used by this project at startup.
Base.metadata.create_all(bind=engine)

# Ensure the users table has the required auth column when the app starts.
ensure_user_schema(engine)

app = FastAPI(
    title="Cyber Defense Center",
    description="A cybersecurity platform for monitoring security events, vulnerabilities, incidents, and threat intelligence.",
    version="1.0.0",
)

# Mount the routers so these API routes are available under the app.
app.include_router(users_router)
app.include_router(incidents_router)


@app.get("/")
def root():
    return {
        "application": "Cyber Defense Center",
        "status": "Running",
        "version": "1.0.0"
    }