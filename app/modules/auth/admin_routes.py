"""
Admin-only routes for user management.
Only SUPER_ADMIN can access these endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.permissions import require_admin
from app.modules.auth.models import User, Role
from app.modules.auth.schema import CreateUser, UpdateUser, UserResponse
from app.modules.auth.service import create_user, update_user, get_user_by_id

router = APIRouter(prefix="/api/admin/users", tags=["Admin - User Management"])


@router.get("", response_model=List[UserResponse])
def list_all_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)  # Only SUPER_ADMIN
):
    """
    Get all users in the system.

    **Required Role:** SUPER_ADMIN
    """
    statement = select(User).where(User.is_deleted == False)
    users = session.exec(statement).all()
    return users


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: CreateUser,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)  # Only SUPER_ADMIN
):
    """
    Create a new user (admin function).

    **Required Role:** SUPER_ADMIN

    Allows creating users with any role and branch assignment.
    """
    user = create_user(session, user_data)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id_admin(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)  # Only SUPER_ADMIN
):
    """
    Get any user by ID.

    **Required Role:** SUPER_ADMIN
    """
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_admin(
    user_id: int,
    user_data: UpdateUser,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)  # Only SUPER_ADMIN
):
    """
    Update any user.

    **Required Role:** SUPER_ADMIN

    Can change roles, activate/deactivate users, etc.
    """
    user = update_user(session, user_id, user_data)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_admin(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)  # Only SUPER_ADMIN
):
    """
    Soft delete a user.

    **Required Role:** SUPER_ADMIN
    """
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Soft delete
    user.is_deleted = True
    session.add(user)
    session.commit()


@router.get("/roles", response_model=List[dict])
def list_all_roles(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)  # Only SUPER_ADMIN
):
    """
    Get all available roles.

    **Required Role:** SUPER_ADMIN
    """
    statement = select(Role).where(Role.is_deleted == False)
    roles = session.exec(statement).all()

    return [
        {
            "id": role.id,
            "name": role.name.value,
            "description": role.description
        }
        for role in roles
    ]
