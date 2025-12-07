from enum import Enum


class UserRole(str, Enum):
    """User roles in the system"""

    # Internal roles
    SUPER_ADMIN = "super_admin"  # Owner: Sees all branches and finances
    BRANCH_MANAGER = "manager"  # Manager: Controls THEIR branch and THEIR stock
    SALES_AGENT = "sales"  # Salesperson: Sells at POS and attends counter
    LOGISTICS = "logistics"  # Shipping handler: Prepares packages
    CUSTOMER = "customer"  # Web buyer: Only sees their orders
