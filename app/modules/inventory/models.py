from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.core.mixins import AuditMixin
from .enums import MovementType

if TYPE_CHECKING:
    from app.modules.auth.models import User
    from app.modules.catalog.models import Product
    from app.modules.sales.models import Order


class Branch(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name_branch: str
    address: str
    phone: int
    can_ship: bool = True

    # Relations
    users: List["User"] = Relationship(back_populates="branch")
    stock_entries: List["StockEntry"] = Relationship(back_populates="branch")
    orders: List["Order"] = Relationship(back_populates="fulfillment_branch")


class StockEntry(AuditMixin, table=True):
    """Tabla Pivot: Total of product X for Branch Y"""

    branch_id: int = Field(foreign_key="branch.id", primary_key=True)
    product_id: int = Field(foreign_key="product.id", primary_key=True)
    quantity: int = Field(default=0)

    # Relationships
    branch: "Branch" = Relationship(back_populates="stock_entries")
    product: "Product" = Relationship(back_populates="stock_entries")


class InventoryMovement(AuditMixin, table=True):
    """Records all inventory movements (in, out, transfers)"""

    id: Optional[int] = Field(default=None, primary_key=True)
    movement_type: MovementType = Field(index=True)
    quantity: int
    notes: Optional[str] = None

    product_id: int = Field(foreign_key="product.id")
    branch_id: int = Field(foreign_key="branch.id")
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")

    # Relationships
    product: "Product" = Relationship()
    branch: "Branch" = Relationship()
    order: Optional["Order"] = Relationship()
