from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.permissions import require_logistics
from app.modules.auth.models import User
from .schema import ShipmentCreate, ShipmentUpdate, ShipmentResponse
from .service import (
    get_shipments,
    get_shipment_by_id,
    get_shipment_by_tracking_number,
    create_shipment,
    update_shipment,
    delete_shipment
)

router = APIRouter(prefix="/api/logistics", tags=["Logistics"])


# ========================================
# Shipment Endpoints
# ========================================

@router.get("/shipments", response_model=List[ShipmentResponse])
def list_shipments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    order_id: Optional[int] = Query(default=None),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_logistics)
):
    """Get all shipments with optional order filter (SUPER_ADMIN or LOGISTICS)"""
    return get_shipments(session, skip, limit, order_id)


@router.get("/shipments/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(
    shipment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_logistics)
):
    """Get a specific shipment by ID (SUPER_ADMIN or LOGISTICS)"""
    shipment = get_shipment_by_id(session, shipment_id)
    if not shipment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.get("/shipments/tracking/{tracking_number}", response_model=ShipmentResponse)
def get_shipment_by_tracking(
    tracking_number: str,
    session: Session = Depends(get_session)
):
    """Get a shipment by tracking number (public)"""
    shipment = get_shipment_by_tracking_number(session, tracking_number)
    if not shipment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.post("/shipments", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED)
def create_new_shipment(
    shipment_data: ShipmentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_logistics)
):
    """Create a new shipment (SUPER_ADMIN or LOGISTICS)"""
    return create_shipment(session, shipment_data)


@router.patch("/shipments/{shipment_id}", response_model=ShipmentResponse)
def update_existing_shipment(
    shipment_id: int,
    shipment_data: ShipmentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_logistics)
):
    """Update a shipment (SUPER_ADMIN or LOGISTICS)"""
    return update_shipment(session, shipment_id, shipment_data)


@router.delete("/shipments/{shipment_id}", status_code=status.HTTP_200_OK)
def delete_existing_shipment(
    shipment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_logistics)
):
    """Delete a shipment (SUPER_ADMIN or LOGISTICS)"""
    return delete_shipment(session, shipment_id)
