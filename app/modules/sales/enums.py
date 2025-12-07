from enum import Enum


class OrderType(str, Enum):
    """Type of order"""
    ONLINE = "ONLINE"
    IN_STORE = "IN_STORE"
    PHONE = "PHONE"


class OrderStatus(str, Enum):
    """Order status"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
