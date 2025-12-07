from sqlmodel import Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from app.core.mixins import AuditMixin

if TYPE_CHECKING:
    from app.modules.inventory.models import StockEntry


class Category(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)

    # Relationships
    products: List["Product"] = Relationship(back_populates="category")

class ProductImage(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    url: str = Field(max_length=500)
    position: int = Field(default=0)
    is_primary: bool = Field(default=False)

    product: "Product" = Relationship(back_populates="images")

class Product(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True, max_length=50)
    name_product: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    price: float

    category_id: int = Field(default=None, foreign_key="category.id")

    # Relationships
    category: Optional["Category"] = Relationship(back_populates="products")
    stock_entries: List["StockEntry"] = Relationship(back_populates="product")
    images: List["ProductImage"] = Relationship(back_populates="product")
