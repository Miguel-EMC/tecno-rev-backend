from enum import Enum


class MovementType(str, Enum):
    """Types of inventory movements"""
    IN = "IN"              # Stock coming in (purchases, returns)
    OUT = "OUT"            # Stock going out (sales)
    TRANSFER = "TRANSFER"  # Transfer between branches
    ADJUSTMENT = "ADJUSTMENT"  # Manual inventory adjustment
