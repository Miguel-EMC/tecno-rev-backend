from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.permissions import require_manager, require_staff
from app.modules.auth.models import User
from .schema import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderItemResponse,
    CouponCreate,
    CouponUpdate,
    CouponResponse
)
from .service import (
    get_orders,
    get_order_by_id,
    create_order,
    update_order,
    delete_order,
    get_order_items,
    get_coupons,
    get_coupon_by_id,
    create_coupon,
    update_coupon,
    delete_coupon,
    apply_coupon_to_order
)

router = APIRouter(prefix="/api/sales", tags=["Sales"])


# ========================================
# Order Endpoints
# ========================================

@router.get("/orders", response_model=List[OrderResponse])
def list_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    customer_id: Optional[int] = Query(default=None),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_staff)
):
    """Get all orders with optional customer filter (SUPER_ADMIN, BRANCH_MANAGER, or SALES_AGENT)"""
    return get_orders(session, skip, limit, customer_id)


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_staff)
):
    """Get a specific order by ID (SUPER_ADMIN, BRANCH_MANAGER, or SALES_AGENT)"""
    order = get_order_by_id(session, order_id)
    if not order:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_new_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_staff)
):
    """Create a new order (SUPER_ADMIN, BRANCH_MANAGER, or SALES_AGENT)"""
    return create_order(session, order_data)


@router.patch("/orders/{order_id}", response_model=OrderResponse)
def update_existing_order(
    order_id: int,
    order_data: OrderUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_staff)
):
    """Update an order (SUPER_ADMIN, BRANCH_MANAGER, or SALES_AGENT)"""
    return update_order(session, order_id, order_data)


@router.delete("/orders/{order_id}", status_code=status.HTTP_200_OK)
def delete_existing_order(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_staff)
):
    """Delete an order (SUPER_ADMIN, BRANCH_MANAGER, or SALES_AGENT)"""
    return delete_order(session, order_id)


@router.get("/orders/{order_id}/items", response_model=List[OrderItemResponse])
def list_order_items(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_staff)
):
    """Get all items for an order (SUPER_ADMIN, BRANCH_MANAGER, or SALES_AGENT)"""
    return get_order_items(session, order_id)


@router.post("/orders/{order_id}/apply-coupon", response_model=OrderResponse)
def apply_coupon(
    order_id: int,
    coupon_code: str = Query(..., min_length=3),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_staff)
):
    """Apply a coupon to an order (SUPER_ADMIN, BRANCH_MANAGER, or SALES_AGENT)"""
    return apply_coupon_to_order(session, order_id, coupon_code)


# ========================================
# Coupon Endpoints
# ========================================

@router.get("/coupons", response_model=List[CouponResponse])
def list_coupons(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Get all coupons (SUPER_ADMIN or BRANCH_MANAGER)"""
    return get_coupons(session, skip, limit)


@router.get("/coupons/{coupon_id}", response_model=CouponResponse)
def get_coupon(
    coupon_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Get a specific coupon by ID (SUPER_ADMIN or BRANCH_MANAGER)"""
    coupon = get_coupon_by_id(session, coupon_id)
    if not coupon:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon


@router.post("/coupons", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_new_coupon(
    coupon_data: CouponCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Create a new coupon (SUPER_ADMIN or BRANCH_MANAGER)"""
    return create_coupon(session, coupon_data)


@router.patch("/coupons/{coupon_id}", response_model=CouponResponse)
def update_existing_coupon(
    coupon_id: int,
    coupon_data: CouponUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Update a coupon (SUPER_ADMIN or BRANCH_MANAGER)"""
    return update_coupon(session, coupon_id, coupon_data)


@router.delete("/coupons/{coupon_id}", status_code=status.HTTP_200_OK)
def delete_existing_coupon(
    coupon_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Delete a coupon (SUPER_ADMIN or BRANCH_MANAGER)"""
    return delete_coupon(session, coupon_id)
