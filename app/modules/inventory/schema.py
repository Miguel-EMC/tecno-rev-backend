from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .enums import MovementType


# Branch Schemas
class BranchCreate(BaseModel):
    """Schema for creating a branch"""
    name_branch: str = Field(min_length=2, max_length=200)
    address: str = Field(max_length=500)
    phone: int
    can_ship: bool = True


class BranchUpdate(BaseModel):
    """Schema for updating a branch"""
    name_branch: Optional[str] = Field(default=None, min_length=2, max_length=200)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[int] = None
    can_ship: Optional[bool] = None


class BranchResponse(BaseModel):
    """Schema for branch response"""
    id: int
    name_branch: str
    address: str
    phone: int
    can_ship: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Stock Entry Schemas
class StockEntryCreate(BaseModel):
    """Schema for creating a stock entry"""
    branch_id: int
    product_id: int
    quantity: int = Field(ge=0, description="Quantity must be >= 0")


class StockEntryUpdate(BaseModel):
    """Schema for updating a stock entry"""
    quantity: int = Field(ge=0, description="Quantity must be >= 0")


class StockEntryResponse(BaseModel):
    """Schema for stock entry response"""
    branch_id: int
    product_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Inventory Movement Schemas
class InventoryMovementCreate(BaseModel):
    """Schema for creating an inventory movement"""
    movement_type: MovementType
    quantity: int = Field(gt=0, description="Quantity must be > 0")
    notes: Optional[str] = Field(default=None, max_length=1000)
    product_id: int
    branch_id: int
    order_id: Optional[int] = None


class InventoryMovementUpdate(BaseModel):
    """Schema for updating an inventory movement"""
    movement_type: Optional[MovementType] = None
    quantity: Optional[int] = Field(default=None, gt=0)
    notes: Optional[str] = Field(default=None, max_length=1000)


class InventoryMovementResponse(BaseModel):
    """Schema for inventory movement response"""
    id: int
    movement_type: MovementType
    quantity: int
    notes: Optional[str]
    product_id: int
    branch_id: int
    order_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
