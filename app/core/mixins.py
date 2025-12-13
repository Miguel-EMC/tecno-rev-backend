from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Returns current UTC time as timezone-aware datetime"""
    return datetime.now(timezone.utc)


class AuditMixin(SQLModel):
    """Mixin for common audit fields"""
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[int] = None
