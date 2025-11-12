from sqlalchemy import Column, Integer, String, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from app.database import Base


class Suscripcion(Base):
    __tablename__ = "suscripciones"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    pisos = Column(ARRAY(Integer), nullable=False)
    niveles = Column(ARRAY(String(20)), nullable=False)
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint("email", name="unique_email"),
    )

