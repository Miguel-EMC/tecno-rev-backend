from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.auth.service import get_current_active_user
from app.modules.auth.models import User
from .schema import (
    BranchCreate,
    BranchUpdate,
    BranchResponse,
    StockEntryCreate,
    StockEntryUpdate,
    StockEntryResponse,
    InventoryMovementCreate,
    InventoryMovementUpdate,
    InventoryMovementResponse
)
from .service import (
    get_branches,
    get_branch_by_id,
    create_branch,
    update_branch,
    delete_branch,
    get_stock_entries,
    get_stock_entry,
    create_stock_entry,
    update_stock_entry,
    delete_stock_entry,
    get_inventory_movements,
    get_inventory_movement_by_id,
    create_inventory_movement,
    update_inventory_movement,
    delete_inventory_movement
)

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


# ========================================
# Branch Endpoints
# ========================================

@router.get("/branches", response_model=List[BranchResponse])
def list_branches(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Get all branches (public)"""
    return get_branches(session, skip, limit)


@router.get("/branches/{branch_id}", response_model=BranchResponse)
def get_branch(
    branch_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific branch by ID (public)"""
    branch = get_branch_by_id(session, branch_id)
    if not branch:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@router.post("/branches", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_new_branch(
    branch_data: BranchCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new branch (protected)"""
    return create_branch(session, branch_data)


@router.patch("/branches/{branch_id}", response_model=BranchResponse)
def update_existing_branch(
    branch_id: int,
    branch_data: BranchUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update a branch (protected)"""
    return update_branch(session, branch_id, branch_data)


@router.delete("/branches/{branch_id}", status_code=status.HTTP_200_OK)
def delete_existing_branch(
    branch_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a branch (protected)"""
    return delete_branch(session, branch_id)


# ========================================
# Stock Entry Endpoints
# ========================================

@router.get("/stock", response_model=List[StockEntryResponse])
def list_stock_entries(
    branch_id: Optional[int] = Query(default=None),
    product_id: Optional[int] = Query(default=None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get stock entries with optional filters (protected)"""
    return get_stock_entries(session, branch_id, product_id)


@router.get("/stock/{branch_id}/{product_id}", response_model=StockEntryResponse)
def get_stock(
    branch_id: int,
    product_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get stock entry for specific branch and product (protected)"""
    stock = get_stock_entry(session, branch_id, product_id)
    if not stock:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Stock entry not found")
    return stock


@router.post("/stock", response_model=StockEntryResponse, status_code=status.HTTP_201_CREATED)
def create_new_stock_entry(
    stock_data: StockEntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new stock entry (protected)"""
    return create_stock_entry(session, stock_data)


@router.patch("/stock/{branch_id}/{product_id}", response_model=StockEntryResponse)
def update_existing_stock_entry(
    branch_id: int,
    product_id: int,
    stock_data: StockEntryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update a stock entry (protected)"""
    return update_stock_entry(session, branch_id, product_id, stock_data)


@router.delete("/stock/{branch_id}/{product_id}", status_code=status.HTTP_200_OK)
def delete_existing_stock_entry(
    branch_id: int,
    product_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a stock entry (protected)"""
    return delete_stock_entry(session, branch_id, product_id)


# ========================================
# Inventory Movement Endpoints
# ========================================

@router.get("/movements", response_model=List[InventoryMovementResponse])
def list_inventory_movements(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    branch_id: Optional[int] = Query(default=None),
    product_id: Optional[int] = Query(default=None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get inventory movements with optional filters (protected)"""
    return get_inventory_movements(session, skip, limit, branch_id, product_id)


@router.get("/movements/{movement_id}", response_model=InventoryMovementResponse)
def get_movement(
    movement_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific inventory movement by ID (protected)"""
    movement = get_inventory_movement_by_id(session, movement_id)
    if not movement:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Inventory movement not found")
    return movement


@router.post("/movements", response_model=InventoryMovementResponse, status_code=status.HTTP_201_CREATED)
def create_new_inventory_movement(
    movement_data: InventoryMovementCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new inventory movement (protected)"""
    return create_inventory_movement(session, movement_data)


@router.patch("/movements/{movement_id}", response_model=InventoryMovementResponse)
def update_existing_inventory_movement(
    movement_id: int,
    movement_data: InventoryMovementUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update an inventory movement (protected)"""
    return update_inventory_movement(session, movement_id, movement_data)


@router.delete("/movements/{movement_id}", status_code=status.HTTP_200_OK)
def delete_existing_inventory_movement(
    movement_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an inventory movement (protected)"""
    return delete_inventory_movement(session, movement_id)
