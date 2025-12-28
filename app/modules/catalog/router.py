from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.core.permissions import require_manager
from app.modules.auth.models import User
from .schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductImageCreate,
    ProductImageUpdate,
    ProductImageResponse
)
from .service import (
    get_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
    get_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
    get_product_images,
    get_product_image_by_id,
    create_product_image,
    update_product_image,
    delete_product_image
)

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])


# ========================================
# Category Endpoints
# ========================================

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Get all categories (public)"""
    return get_categories(session, skip, limit)


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific category by ID (public)"""
    category = get_category_by_id(session, category_id)
    if not category:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category_data: CategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Create a new category (SUPER_ADMIN or BRANCH_MANAGER only)"""
    return create_category(session, category_data)


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_existing_category(
    category_id: int,
    category_data: CategoryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Update a category (SUPER_ADMIN or BRANCH_MANAGER only)"""
    return update_category(session, category_id, category_data)


@router.delete("/categories/{category_id}", status_code=status.HTTP_200_OK)
def delete_existing_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Delete a category (SUPER_ADMIN or BRANCH_MANAGER only)"""
    return delete_category(session, category_id)


# ========================================
# Product Endpoints
# ========================================

@router.get("/products", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    category_id: Optional[int] = Query(default=None),
    session: Session = Depends(get_session)
):
    """Get all products with optional category filter (public)"""
    return get_products(session, skip, limit, category_id)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific product by ID (public)"""
    product = get_product_by_id(session, product_id)
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_new_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Create a new product (SUPER_ADMIN or BRANCH_MANAGER only)"""
    return create_product(session, product_data)


@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_existing_product(
    product_id: int,
    product_data: ProductUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Update a product (SUPER_ADMIN or BRANCH_MANAGER only)"""
    return update_product(session, product_id, product_data)


@router.delete("/products/{product_id}", status_code=status.HTTP_200_OK)
def delete_existing_product(
    product_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Delete a product (SUPER_ADMIN or BRANCH_MANAGER only)"""
    return delete_product(session, product_id)


# ========================================
# Product Image Endpoints
# ========================================

@router.get("/products/{product_id}/images", response_model=List[ProductImageResponse])
def list_product_images(
    product_id: int,
    session: Session = Depends(get_session)
):
    """Get all images for a product (public)"""
    return get_product_images(session, product_id)


@router.get("/images/{image_id}", response_model=ProductImageResponse)
def get_image(
    image_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific product image by ID (public)"""
    image = get_product_image_by_id(session, image_id)
    if not image:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product image not found")
    return image


@router.post("/images", response_model=ProductImageResponse, status_code=status.HTTP_201_CREATED)
def create_new_product_image(
    image_data: ProductImageCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Create a new product image (SUPER_ADMIN or BRANCH_MANAGER only)"""
    return create_product_image(session, image_data)


@router.patch("/images/{image_id}", response_model=ProductImageResponse)
def update_existing_product_image(
    image_id: int,
    image_data: ProductImageUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Update a product image (SUPER_ADMIN or BRANCH_MANAGER only)"""
    return update_product_image(session, image_id, image_data)


@router.delete("/images/{image_id}", status_code=status.HTTP_200_OK)
def delete_existing_product_image(
    image_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_manager)
):
    """Delete a product image (SUPER_ADMIN or BRANCH_MANAGER only)"""
    return delete_product_image(session, image_id)
