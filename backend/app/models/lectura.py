from sqlalchemy import Column, Integer, String, Numeric, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class Lectura(Base):
    __tablename__ = "lecturas"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    edificio = Column(String(10), nullable=False, default="A")
    piso = Column(Integer, nullable=False, index=True)
    temp_c = Column(Numeric(5, 2), nullable=False)
    humedad_pct = Column(Numeric(5, 2), nullable=False)
    energia_kw = Column(Numeric(8, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("piso IN (1, 2, 3)", name="check_piso"),
        UniqueConstraint("timestamp", "edificio", "piso", name="unique_reading"),
    )

