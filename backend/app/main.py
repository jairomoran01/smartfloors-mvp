from fastapi import FastAPI
from app.routes import readings, alerts

app = FastAPI(title="SmartFloors API", version="1.0")

app.include_router(readings.router, prefix="/api/v1/readings", tags=["Readings"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])

@app.get("/")
def root():
    return {"status": "SmartFloors API running 🚀"}
