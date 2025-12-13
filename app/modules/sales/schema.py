from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .enums import OrderType, OrderStatus


# Order Item Schemas
class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be > 0")
    unit_price: float = Field(gt=0, description="Price must be > 0")


class OrderItemResponse(BaseModel):
    """Schema for order item response"""
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Order Schemas
class OrderCreate(BaseModel):
    """Schema for creating an order"""
    tracking_number: str = Field(min_length=5, max_length=100)
    order_type: OrderType
    shipping_address: Optional[str] = Field(default=None, max_length=500)
    customer_id: Optional[int] = None
    fulfillment_branch_id: int
    items: list[OrderItemCreate] = Field(min_items=1)


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = Field(default=None, max_length=500)
    discount_amount: Optional[float] = Field(default=None, ge=0)


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: int
    tracking_number: str
    total_amount: float
    discount_amount: float
    order_type: OrderType
    status: OrderStatus
    total_items: int
    subtotal: float
    shipping_address: Optional[str]
    customer_id: Optional[int]
    fulfillment_branch_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Coupon Schemas
class CouponCreate(BaseModel):
    """Schema for creating a coupon"""
    code: str = Field(min_length=3, max_length=50)
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    discount_amount: Optional[float] = Field(default=None, ge=0)
    max_uses: Optional[int] = Field(default=None, ge=1)
    is_active: bool = True
    expires_at: Optional[str] = None


class CouponUpdate(BaseModel):
    """Schema for updating a coupon"""
    code: Optional[str] = Field(default=None, min_length=3, max_length=50)
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    discount_amount: Optional[float] = Field(default=None, ge=0)
    max_uses: Optional[int] = Field(default=None, ge=1)
    is_active: Optional[bool] = None
    expires_at: Optional[str] = None


class CouponResponse(BaseModel):
    """Schema for coupon response"""
    id: int
    code: str
    discount_percentage: Optional[float]
    discount_amount: Optional[float]
    max_uses: Optional[int]
    current_uses: int
    is_active: bool
    expires_at: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
