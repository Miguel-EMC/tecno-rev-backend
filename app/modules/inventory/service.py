from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status

from .models import Branch, StockEntry, InventoryMovement
from .schema import (
    BranchCreate,
    BranchUpdate,
    StockEntryCreate,
    StockEntryUpdate,
    InventoryMovementCreate,
    InventoryMovementUpdate
)


# ========================================
# Branch CRUD Operations
# ========================================

def get_branches(session: Session, skip: int = 0, limit: int = 100) -> List[Branch]:
    """Get all branches with pagination"""
    statement = select(Branch).where(not Branch.is_deleted).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_branch_by_id(session: Session, branch_id: int) -> Optional[Branch]:
    """Get a branch by ID"""
    statement = select(Branch).where(Branch.id == branch_id, not Branch.is_deleted)
    return session.exec(statement).first()


def create_branch(session: Session, branch_data: BranchCreate) -> Branch:
    """Create a new branch"""
    branch = Branch(**branch_data.model_dump())
    session.add(branch)
    session.commit()
    session.refresh(branch)
    return branch


def update_branch(session: Session, branch_id: int, branch_data: BranchUpdate) -> Branch:
    """Update an existing branch"""
    branch = get_branch_by_id(session, branch_id)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )

    update_data = branch_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)

    session.add(branch)
    session.commit()
    session.refresh(branch)
    return branch


def delete_branch(session: Session, branch_id: int) -> dict:
    """Soft delete a branch"""
    branch = get_branch_by_id(session, branch_id)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )

    branch.is_deleted = True
    session.add(branch)
    session.commit()
    return {"message": "Branch deleted successfully"}


# ========================================
# Stock Entry CRUD Operations
# ========================================

def get_stock_entries(
    session: Session,
    branch_id: Optional[int] = None,
    product_id: Optional[int] = None
) -> List[StockEntry]:
    """Get stock entries with optional filters"""
    statement = select(StockEntry).where(not StockEntry.is_deleted)

    if branch_id:
        statement = statement.where(StockEntry.branch_id == branch_id)
    if product_id:
        statement = statement.where(StockEntry.product_id == product_id)

    return list(session.exec(statement).all())


def get_stock_entry(session: Session, branch_id: int, product_id: int) -> Optional[StockEntry]:
    """Get stock entry by branch and product"""
    statement = select(StockEntry).where(
        StockEntry.branch_id == branch_id,
        StockEntry.product_id == product_id,
        not StockEntry.is_deleted
    )
    return session.exec(statement).first()


def create_stock_entry(session: Session, stock_data: StockEntryCreate) -> StockEntry:
    """Create a new stock entry"""
    # Check if stock entry already exists
    existing = get_stock_entry(session, stock_data.branch_id, stock_data.product_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock entry already exists for this branch and product"
        )

    # Verify branch exists
    branch = get_branch_by_id(session, stock_data.branch_id)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )

    stock_entry = StockEntry(**stock_data.model_dump())
    session.add(stock_entry)
    session.commit()
    session.refresh(stock_entry)
    return stock_entry


def update_stock_entry(
    session: Session,
    branch_id: int,
    product_id: int,
    stock_data: StockEntryUpdate
) -> StockEntry:
    """Update an existing stock entry"""
    stock_entry = get_stock_entry(session, branch_id, product_id)
    if not stock_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock entry not found"
        )

    update_data = stock_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stock_entry, field, value)

    session.add(stock_entry)
    session.commit()
    session.refresh(stock_entry)
    return stock_entry


def delete_stock_entry(session: Session, branch_id: int, product_id: int) -> dict:
    """Soft delete a stock entry"""
    stock_entry = get_stock_entry(session, branch_id, product_id)
    if not stock_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock entry not found"
        )

    stock_entry.is_deleted = True
    session.add(stock_entry)
    session.commit()
    return {"message": "Stock entry deleted successfully"}


# ========================================
# Inventory Movement CRUD Operations
# ========================================

def get_inventory_movements(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    branch_id: Optional[int] = None,
    product_id: Optional[int] = None
) -> List[InventoryMovement]:
    """Get inventory movements with optional filters"""
    statement = select(InventoryMovement).where(not InventoryMovement.is_deleted)

    if branch_id:
        statement = statement.where(InventoryMovement.branch_id == branch_id)
    if product_id:
        statement = statement.where(InventoryMovement.product_id == product_id)

    statement = statement.offset(skip).limit(limit).order_by(InventoryMovement.created_at.desc())
    return list(session.exec(statement).all())


def get_inventory_movement_by_id(session: Session, movement_id: int) -> Optional[InventoryMovement]:
    """Get an inventory movement by ID"""
    statement = select(InventoryMovement).where(
        InventoryMovement.id == movement_id,
        not InventoryMovement.is_deleted
    )
    return session.exec(statement).first()


def create_inventory_movement(session: Session, movement_data: InventoryMovementCreate) -> InventoryMovement:
    """Create a new inventory movement"""
    # Verify branch exists
    branch = get_branch_by_id(session, movement_data.branch_id)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )

    # Create movement
    movement = InventoryMovement(**movement_data.model_dump())
    session.add(movement)
    session.commit()
    session.refresh(movement)

    # Update stock entry
    stock_entry = get_stock_entry(session, movement_data.branch_id, movement_data.product_id)
    if stock_entry:
        # Update existing stock
        if movement.movement_type.value in ["IN", "ADJUSTMENT"]:
            stock_entry.quantity += movement.quantity
        elif movement.movement_type.value in ["OUT"]:
            stock_entry.quantity -= movement.quantity
            if stock_entry.quantity < 0:
                stock_entry.quantity = 0  # Prevent negative stock

        session.add(stock_entry)
        session.commit()
    else:
        # Create new stock entry if movement is IN
        if movement.movement_type.value in ["IN", "ADJUSTMENT"]:
            new_stock = StockEntry(
                branch_id=movement_data.branch_id,
                product_id=movement_data.product_id,
                quantity=movement.quantity
            )
            session.add(new_stock)
            session.commit()

    return movement


def update_inventory_movement(
    session: Session,
    movement_id: int,
    movement_data: InventoryMovementUpdate
) -> InventoryMovement:
    """Update an existing inventory movement"""
    movement = get_inventory_movement_by_id(session, movement_id)
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory movement not found"
        )

    update_data = movement_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(movement, field, value)

    session.add(movement)
    session.commit()
    session.refresh(movement)
    return movement


def delete_inventory_movement(session: Session, movement_id: int) -> dict:
    """Soft delete an inventory movement"""
    movement = get_inventory_movement_by_id(session, movement_id)
    if not movement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory movement not found"
        )

    movement.is_deleted = True
    session.add(movement)
    session.commit()
    return {"message": "Inventory movement deleted successfully"}
