from enum import Enum


class UserRole(str, Enum):
    """User roles in the system"""

    # Internal roles
    SUPER_ADMIN = "SUPER_ADMIN"  # Owner: Sees all branches and finances
    BRANCH_MANAGER = "BRANCH_MANAGER"  # Manager: Controls THEIR branch and THEIR stock
    SALES_AGENT = "SALES_AGENT"  # Salesperson: Sells at POS and attends counter
    LOGISTICS = "LOGISTICS"  # Shipping handler: Prepares packages
    CUSTOMER = "CUSTOMER"  # Web buyer: Only sees their orders
