from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status

from .models import Order, OrderItem, Coupon
from .schema import OrderCreate, OrderUpdate, CouponCreate, CouponUpdate, OrderItemCreate


# ========================================
# Order CRUD Operations
# ========================================

def get_orders(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[int] = None
) -> List[Order]:
    """Get all orders with optional customer filter"""
    statement = select(Order).where(not Order.is_deleted)

    if customer_id:
        statement = statement.where(Order.customer_id == customer_id)

    statement = statement.offset(skip).limit(limit).order_by(Order.created_at.desc())
    return list(session.exec(statement).all())


def get_order_by_id(session: Session, order_id: int) -> Optional[Order]:
    """Get an order by ID"""
    statement = select(Order).where(Order.id == order_id, not Order.is_deleted)
    return session.exec(statement).first()


def get_order_by_tracking_number(session: Session, tracking_number: str) -> Optional[Order]:
    """Get an order by tracking number"""
    statement = select(Order).where(
        Order.tracking_number == tracking_number,
        not Order.is_deleted
    )
    return session.exec(statement).first()


def create_order(session: Session, order_data: OrderCreate) -> Order:
    """Create a new order with items"""
    # Check if tracking number already exists
    existing = get_order_by_tracking_number(session, order_data.tracking_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order with tracking number '{order_data.tracking_number}' already exists"
        )

    # Calculate totals
    subtotal = sum(item.quantity * item.unit_price for item in order_data.items)
    total_items = sum(item.quantity for item in order_data.items)

    # Create order (without items first)
    order_dict = order_data.model_dump(exclude={"items"})
    order = Order(
        **order_dict,
        subtotal=subtotal,
        total_amount=subtotal,
        total_items=total_items
    )

    session.add(order)
    session.commit()
    session.refresh(order)

    # Create order items
    for item_data in order_data.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price
        )
        session.add(order_item)

    session.commit()
    session.refresh(order)
    return order


def update_order(session: Session, order_id: int, order_data: OrderUpdate) -> Order:
    """Update an existing order"""
    order = get_order_by_id(session, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    update_data = order_data.model_dump(exclude_unset=True)

    # Recalculate total if discount changed
    if "discount_amount" in update_data:
        order.total_amount = order.subtotal - update_data["discount_amount"]

    for field, value in update_data.items():
        setattr(order, field, value)

    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def delete_order(session: Session, order_id: int) -> dict:
    """Soft delete an order"""
    order = get_order_by_id(session, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order.is_deleted = True
    session.add(order)
    session.commit()
    return {"message": "Order deleted successfully"}


# ========================================
# Order Item Operations
# ========================================

def get_order_items(session: Session, order_id: int) -> List[OrderItem]:
    """Get all items for an order"""
    statement = select(OrderItem).where(
        OrderItem.order_id == order_id,
        not OrderItem.is_deleted
    )
    return list(session.exec(statement).all())


# ========================================
# Coupon CRUD Operations
# ========================================

def get_coupons(session: Session, skip: int = 0, limit: int = 100) -> List[Coupon]:
    """Get all coupons with pagination"""
    statement = select(Coupon).where(not Coupon.is_deleted).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_coupon_by_id(session: Session, coupon_id: int) -> Optional[Coupon]:
    """Get a coupon by ID"""
    statement = select(Coupon).where(Coupon.id == coupon_id, not Coupon.is_deleted)
    return session.exec(statement).first()


def get_coupon_by_code(session: Session, code: str) -> Optional[Coupon]:
    """Get a coupon by code"""
    statement = select(Coupon).where(Coupon.code == code, not Coupon.is_deleted)
    return session.exec(statement).first()


def create_coupon(session: Session, coupon_data: CouponCreate) -> Coupon:
    """Create a new coupon"""
    # Check if coupon code already exists
    existing = get_coupon_by_code(session, coupon_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Coupon with code '{coupon_data.code}' already exists"
        )

    # Validate that either percentage or amount is set, not both
    if coupon_data.discount_percentage and coupon_data.discount_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon cannot have both percentage and amount discount"
        )

    if not coupon_data.discount_percentage and not coupon_data.discount_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon must have either percentage or amount discount"
        )

    coupon = Coupon(**coupon_data.model_dump())
    session.add(coupon)
    session.commit()
    session.refresh(coupon)
    return coupon


def update_coupon(session: Session, coupon_id: int, coupon_data: CouponUpdate) -> Coupon:
    """Update an existing coupon"""
    coupon = get_coupon_by_id(session, coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )

    update_data = coupon_data.model_dump(exclude_unset=True)

    # Check if new code conflicts
    if "code" in update_data:
        existing = get_coupon_by_code(session, update_data["code"])
        if existing and existing.id != coupon_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Coupon with code '{update_data['code']}' already exists"
            )

    for field, value in update_data.items():
        setattr(coupon, field, value)

    session.add(coupon)
    session.commit()
    session.refresh(coupon)
    return coupon


def delete_coupon(session: Session, coupon_id: int) -> dict:
    """Soft delete a coupon"""
    coupon = get_coupon_by_id(session, coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )

    coupon.is_deleted = True
    session.add(coupon)
    session.commit()
    return {"message": "Coupon deleted successfully"}


def apply_coupon_to_order(session: Session, order_id: int, coupon_code: str) -> Order:
    """Apply a coupon to an order"""
    order = get_order_by_id(session, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    coupon = get_coupon_by_code(session, coupon_code)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )

    # Validate coupon
    if not coupon.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon is not active"
        )

    if coupon.max_uses and coupon.current_uses >= coupon.max_uses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon usage limit reached"
        )

    # Calculate discount
    if coupon.discount_percentage:
        discount = order.subtotal * (coupon.discount_percentage / 100)
    else:
        discount = coupon.discount_amount or 0

    # Apply discount
    order.discount_amount = discount
    order.total_amount = order.subtotal - discount

    # Increment coupon usage
    coupon.current_uses += 1

    session.add(order)
    session.add(coupon)
    session.commit()
    session.refresh(order)

    return order
