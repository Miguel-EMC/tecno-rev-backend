from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status

from .models import Shipment
from .schema import ShipmentCreate, ShipmentUpdate


# ========================================
# Shipment CRUD Operations
# ========================================

def get_shipments(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    order_id: Optional[int] = None
) -> List[Shipment]:
    """Get all shipments with optional order filter"""
    statement = select(Shipment).where(not Shipment.is_deleted)

    if order_id:
        statement = statement.where(Shipment.order_id == order_id)

    statement = statement.offset(skip).limit(limit).order_by(Shipment.created_at.desc())
    return list(session.exec(statement).all())


def get_shipment_by_id(session: Session, shipment_id: int) -> Optional[Shipment]:
    """Get a shipment by ID"""
    statement = select(Shipment).where(Shipment.id == shipment_id, not Shipment.is_deleted)
    return session.exec(statement).first()


def get_shipment_by_tracking_number(session: Session, tracking_number: str) -> Optional[Shipment]:
    """Get a shipment by tracking number"""
    statement = select(Shipment).where(
        Shipment.tracking_number == tracking_number,
        not Shipment.is_deleted
    )
    return session.exec(statement).first()


def get_shipment_by_order_id(session: Session, order_id: int) -> Optional[Shipment]:
    """Get shipment for a specific order"""
    statement = select(Shipment).where(
        Shipment.order_id == order_id,
        not Shipment.is_deleted
    )
    return session.exec(statement).first()


def create_shipment(session: Session, shipment_data: ShipmentCreate) -> Shipment:
    """Create a new shipment"""
    # Check if tracking number already exists
    existing = get_shipment_by_tracking_number(session, shipment_data.tracking_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Shipment with tracking number '{shipment_data.tracking_number}' already exists"
        )

    # Check if order already has a shipment (one-to-one relationship)
    existing_shipment = get_shipment_by_order_id(session, shipment_data.order_id)
    if existing_shipment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order {shipment_data.order_id} already has a shipment"
        )

    shipment = Shipment(**shipment_data.model_dump())
    session.add(shipment)
    session.commit()
    session.refresh(shipment)
    return shipment


def update_shipment(session: Session, shipment_id: int, shipment_data: ShipmentUpdate) -> Shipment:
    """Update an existing shipment"""
    shipment = get_shipment_by_id(session, shipment_id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )

    update_data = shipment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shipment, field, value)

    session.add(shipment)
    session.commit()
    session.refresh(shipment)
    return shipment


def delete_shipment(session: Session, shipment_id: int) -> dict:
    """Soft delete a shipment"""
    shipment = get_shipment_by_id(session, shipment_id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )

    shipment.is_deleted = True
    session.add(shipment)
    session.commit()
    return {"message": "Shipment deleted successfully"}
