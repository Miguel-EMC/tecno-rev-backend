from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .enums import ShipmentStatus


# Shipment Schemas
class ShipmentCreate(BaseModel):
    """Schema for creating a shipment"""
    tracking_number: str = Field(min_length=5, max_length=100)
    carrier: str = Field(min_length=2, max_length=100)
    shipping_cost: float = Field(ge=0, description="Cost must be >= 0")
    shipping_address: str = Field(max_length=500)
    estimated_delivery_date: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=1000)
    order_id: int
    origin_branch_id: int


class ShipmentUpdate(BaseModel):
    """Schema for updating a shipment"""
    carrier: Optional[str] = Field(default=None, min_length=2, max_length=100)
    status: Optional[ShipmentStatus] = None
    shipping_cost: Optional[float] = Field(default=None, ge=0)
    shipping_address: Optional[str] = Field(default=None, max_length=500)
    estimated_delivery_date: Optional[datetime] = None
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=1000)


class ShipmentResponse(BaseModel):
    """Schema for shipment response"""
    id: int
    tracking_number: str
    carrier: str
    status: ShipmentStatus
    shipping_cost: float
    shipping_address: str
    estimated_delivery_date: Optional[datetime]
    shipped_date: Optional[datetime]
    delivered_date: Optional[datetime]
    notes: Optional[str]
    order_id: int
    origin_branch_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
