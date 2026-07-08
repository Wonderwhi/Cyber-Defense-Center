from fastapi import FastAPI

app = FastAPI(
    title="Cyber Defense Center",
    description="A cybersecurity platform for monitoring security events, vulnerabilities, incidents, and threat intelligence.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "application": "Cyber Defense Center",
        "status": "Running",
        "version": "1.0.0"
    }