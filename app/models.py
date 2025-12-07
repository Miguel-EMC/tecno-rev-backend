"""
Central import for all SQLModel models.
This ensures Alembic can detect all models for migrations.
"""

from app.modules.auth.models import User, Role
from app.modules.catalog.models import Category, Product, ProductImage
from app.modules.inventory.models import Branch, StockEntry, InventoryMovement
from app.modules.sales.models import Order, OrderItem, Coupon
from app.modules.logistics.models import Shipment

__all__ = [
    "User",
    "Role",
    "Category",
    "Product",
    "ProductImage",
    "Branch",
    "StockEntry",
    "InventoryMovement",
    "Order",
    "OrderItem",
    "Coupon",
    "Shipment",
]
