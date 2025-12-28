"""
Role-based permission system for route protection.
"""

from typing import List
from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.auth.models import User
from app.modules.auth.enums import UserRole
from app.modules.auth.service import get_current_active_user


class PermissionChecker:
    """Dependency class to check if user has required roles"""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
        session: Session = Depends(get_session)
    ) -> User:
        """Check if current user's role is in allowed roles"""

        if current_user.role.name not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in self.allowed_roles]}"
            )

        return current_user


# Pre-defined permission checkers for common scenarios

# Admin only (SUPER_ADMIN)
require_admin = PermissionChecker([UserRole.SUPER_ADMIN])

# Admin or Branch Manager
require_manager = PermissionChecker([
    UserRole.SUPER_ADMIN,
    UserRole.BRANCH_MANAGER
])

# Staff (Admin, Manager, Sales)
require_staff = PermissionChecker([
    UserRole.SUPER_ADMIN,
    UserRole.BRANCH_MANAGER,
    UserRole.SALES_AGENT
])

# Logistics staff
require_logistics = PermissionChecker([
    UserRole.SUPER_ADMIN,
    UserRole.LOGISTICS
])

# Any authenticated user (all roles)
require_authenticated = PermissionChecker([
    UserRole.SUPER_ADMIN,
    UserRole.BRANCH_MANAGER,
    UserRole.SALES_AGENT,
    UserRole.LOGISTICS,
    UserRole.CUSTOMER
])


def require_role(role: UserRole):
    """Create a permission checker for a specific role"""
    return PermissionChecker([role])


def require_any_role(*roles: UserRole):
    """Create a permission checker that allows any of the specified roles"""
    return PermissionChecker(list(roles))
