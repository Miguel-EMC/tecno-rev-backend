from enum import Enum


class ShipmentStatus(str, Enum):
    """Shipment status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    IN_TRANSIT = "IN_TRANSIT"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    RETURNED = "RETURNED"
