from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.core.mixins import AuditMixin
from .enums import UserRole

if TYPE_CHECKING:
    from app.modules.inventory.models import Branch
    from app.modules.sales.models import Order


class User(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    phone: int
    hashed_password: str
    is_active: bool = True

    role_id: int = Field(default=None, foreign_key="role.id")
    branch_id: Optional[int] = Field(default=None, foreign_key="branch.id")

    # Relationships
    role: Optional["Role"] = Relationship(back_populates="users")
    branch: Optional["Branch"] = Relationship(back_populates="users")
    orders: List["Order"] = Relationship(back_populates="customer")


class Role(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: UserRole = Field(index=True, unique=True)
    description: Optional[str] = Field(default=None, max_length=2000)

    # Relationships
    users: List["User"] = Relationship(back_populates="role")
