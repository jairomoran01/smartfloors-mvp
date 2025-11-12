from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.notification import NotificationSubscribe, NotificationSubscribeResponse
from app.models.suscripcion import Suscripcion

router = APIRouter()


@router.post("/subscribe", response_model=NotificationSubscribeResponse)
async def subscribe_notifications(
    subscription: NotificationSubscribe,
    db: Session = Depends(get_db)
):
    """Suscribe un email para recibir notificaciones"""
    # Verificar si ya existe
    existing = db.query(Suscripcion).filter(
        Suscripcion.email == subscription.email
    ).first()
    
    if existing:
        # Actualizar suscripción existente
        existing.pisos = subscription.pisos
        existing.niveles = subscription.niveles
        existing.activa = True
        db.commit()
        return NotificationSubscribeResponse(
            message="Suscripción actualizada",
            email=subscription.email,
            subscribed=True
        )
    
    # Crear nueva suscripción
    new_subscription = Suscripcion(
        email=subscription.email,
        pisos=subscription.pisos,
        niveles=subscription.niveles,
        activa=True
    )
    
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    
    return NotificationSubscribeResponse(
        message="Suscripción creada exitosamente",
        email=subscription.email,
        subscribed=True
    )

