from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, Relationship
from app.core.mixins import AuditMixin
from .enums import ShipmentStatus

if TYPE_CHECKING:
    from app.modules.sales.models import Order
    from app.modules.inventory.models import Branch


class Shipment(AuditMixin, table=True):
    """Shipment information for orders"""
    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_number: str = Field(unique=True, index=True)
    carrier: str  # e.g., "DHL", "FedEx", "UPS"
    status: ShipmentStatus = Field(default=ShipmentStatus.PENDING)
    shipping_cost: float = Field(default=0.0)
    shipping_address: str
    estimated_delivery_date: Optional[datetime] = None
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    notes: Optional[str] = None

    # Foreign Keys
    order_id: int = Field(foreign_key="order.id", unique=True)
    origin_branch_id: int = Field(foreign_key="branch.id")

    # Relationships
    order: "Order" = Relationship(back_populates="shipment")
    origin_branch: "Branch" = Relationship()

