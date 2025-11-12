from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class Umbral(Base):
    __tablename__ = "umbrales"
    
    id = Column(Integer, primary_key=True, index=True)
    variable = Column(String(50), nullable=False)
    nivel = Column(String(20), nullable=False)
    valor_min = Column(Numeric(8, 2), nullable=True)
    valor_max = Column(Numeric(8, 2), nullable=True)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

