from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.core.mixins import AuditMixin
from .enums import OrderType, OrderStatus

if TYPE_CHECKING:
    from app.modules.auth.models import User
    from app.modules.inventory.models import Branch
    from app.modules.catalog.models import Product
    from app.modules.logistics.models import Shipment

class Order(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_number: str = Field(unique=True, index=True)
    total_amount: float
    discount_amount: float = 0.0
    order_type: OrderType
    status: OrderStatus = Field(default=OrderStatus.PENDING, index=True)
    total_items: int = Field(default=0)
    subtotal: float = Field(default=0.0)
    shipping_address: Optional[str] = None

    customer_id: Optional[int] = Field(default=None, foreign_key="user.id")
    fulfillment_branch_id: int = Field(foreign_key="branch.id")

    # Relationships
    customer: Optional["User"] = Relationship(back_populates="orders")
    fulfillment_branch: "Branch" = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")
    shipment: Optional["Shipment"] = Relationship(back_populates="order")


class OrderItem(AuditMixin, table=True):
    """Items in an order"""
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    unit_price: float

    # Relationships
    order: "Order" = Relationship(back_populates="items")
    product: "Product" = Relationship()


class Coupon(AuditMixin, table=True):
    """Discount coupons"""
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    max_uses: Optional[int] = None
    current_uses: int = Field(default=0)
    is_active: bool = Field(default=True)
    expires_at: Optional[str] = None
