from fastapi import FastAPI

from app.database.database import Base, engine, ensure_user_schema
from app.routers.users import router as users_router

Base.metadata.create_all(bind=engine)
ensure_user_schema(engine)

app = FastAPI(
    title="Cyber Defense Center",
    description="A cybersecurity platform for monitoring security events, vulnerabilities, incidents, and threat intelligence.",
    version="1.0.0",
)

app.include_router(users_router)


@app.get("/")
def root():
    return {
        "application": "Cyber Defense Center",
        "status": "Running",
        "version": "1.0.0"
    }