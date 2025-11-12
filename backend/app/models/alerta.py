from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Alerta(Base):
    __tablename__ = "alertas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    piso = Column(Integer, nullable=False, index=True)
    variable = Column(String(50), nullable=False)
    nivel = Column(String(20), nullable=False, index=True)
    valor_actual = Column(Numeric(8, 2))
    umbral = Column(Numeric(8, 2))
    recomendacion = Column(Text, nullable=False)
    explicacion = Column(Text)
    estado = Column(String(20), default="activa", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        CheckConstraint("piso IN (1, 2, 3)", name="check_piso"),
        CheckConstraint("nivel IN ('informativa', 'media', 'critica')", name="check_nivel"),
        CheckConstraint("estado IN ('activa', 'reconocida', 'resuelta')", name="check_estado"),
    )

