from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Category Schemas
class CategoryCreate(BaseModel):
    """Schema for creating a category"""
    name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class CategoryResponse(BaseModel):
    """Schema for category response"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Product Schemas
class ProductCreate(BaseModel):
    """Schema for creating a product"""
    sku: str = Field(min_length=3, max_length=50)
    name_product: str = Field(min_length=2, max_length=200)
    description: str = Field(max_length=2000)
    price: float = Field(gt=0, description="Price must be greater than 0")
    category_id: int


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    sku: Optional[str] = Field(default=None, min_length=3, max_length=50)
    name_product: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    price: Optional[float] = Field(default=None, gt=0)
    category_id: Optional[int] = None


class ProductResponse(BaseModel):
    """Schema for product response"""
    id: int
    sku: str
    name_product: str
    description: str
    price: float
    category_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Product Image Schemas
class ProductImageCreate(BaseModel):
    """Schema for creating a product image"""
    product_id: int
    url: str = Field(max_length=500)
    position: int = Field(default=0)
    is_primary: bool = Field(default=False)


class ProductImageUpdate(BaseModel):
    """Schema for updating a product image"""
    url: Optional[str] = Field(default=None, max_length=500)
    position: Optional[int] = None
    is_primary: Optional[bool] = None


class ProductImageResponse(BaseModel):
    """Schema for product image response"""
    id: int
    product_id: int
    url: str
    position: int
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
