from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.lectura import Lectura

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_reading(data: dict, db: Session = Depends(get_db)):
    lectura = Lectura(**data)
    db.add(lectura)
    db.commit()
    return {"status": "created"}
