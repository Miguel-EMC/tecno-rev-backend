from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status

from .models import Category, Product, ProductImage
from .schema import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate, ProductImageCreate, ProductImageUpdate


# ========================================
# Category CRUD Operations
# ========================================

def get_categories(session: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """Get all categories with pagination"""
    statement = select(Category).where(not Category.is_deleted).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_category_by_id(session: Session, category_id: int) -> Optional[Category]:
    """Get a category by ID"""
    statement = select(Category).where(Category.id == category_id, not Category.is_deleted)
    return session.exec(statement).first()


def get_category_by_name(session: Session, name: str) -> Optional[Category]:
    """Get a category by name"""
    statement = select(Category).where(Category.name == name, not Category.is_deleted)
    return session.exec(statement).first()


def create_category(session: Session, category_data: CategoryCreate) -> Category:
    """Create a new category"""
    # Check if category with same name already exists
    existing = get_category_by_name(session, category_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_data.name}' already exists"
        )

    category = Category(**category_data.model_dump())
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def update_category(session: Session, category_id: int, category_data: CategoryUpdate) -> Category:
    """Update an existing category"""
    category = get_category_by_id(session, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if new name conflicts with existing category
    update_data = category_data.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = get_category_by_name(session, update_data["name"])
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{update_data['name']}' already exists"
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def delete_category(session: Session, category_id: int) -> dict:
    """Soft delete a category"""
    category = get_category_by_id(session, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Check if category has products
    statement = select(Product).where(Product.category_id == category_id, not Product.is_deleted)
    products = session.exec(statement).all()
    if products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category. It has {len(products)} active products."
        )

    category.is_deleted = True
    session.add(category)
    session.commit()
    return {"message": "Category deleted successfully"}


# ========================================
# Product CRUD Operations
# ========================================

def get_products(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None
) -> List[Product]:
    """Get all products with optional category filter"""
    statement = select(Product).where(not Product.is_deleted)

    if category_id:
        statement = statement.where(Product.category_id == category_id)

    statement = statement.offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_product_by_id(session: Session, product_id: int) -> Optional[Product]:
    """Get a product by ID"""
    statement = select(Product).where(Product.id == product_id, not Product.is_deleted)
    return session.exec(statement).first()


def get_product_by_sku(session: Session, sku: str) -> Optional[Product]:
    """Get a product by SKU"""
    statement = select(Product).where(Product.sku == sku, not Product.is_deleted)
    return session.exec(statement).first()


def create_product(session: Session, product_data: ProductCreate) -> Product:
    """Create a new product"""
    # Check if SKU already exists
    existing = get_product_by_sku(session, product_data.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product_data.sku}' already exists"
        )

    # Verify category exists
    category = get_category_by_id(session, product_data.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    product = Product(**product_data.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def update_product(session: Session, product_id: int, product_data: ProductUpdate) -> Product:
    """Update an existing product"""
    product = get_product_by_id(session, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_data.model_dump(exclude_unset=True)

    # Check if new SKU conflicts
    if "sku" in update_data:
        existing = get_product_by_sku(session, update_data["sku"])
        if existing and existing.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{update_data['sku']}' already exists"
            )

    # Verify new category exists if being updated
    if "category_id" in update_data:
        category = get_category_by_id(session, update_data["category_id"])
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def delete_product(session: Session, product_id: int) -> dict:
    """Soft delete a product"""
    product = get_product_by_id(session, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product.is_deleted = True
    session.add(product)
    session.commit()
    return {"message": "Product deleted successfully"}


# ========================================
# Product Image CRUD Operations
# ========================================

def get_product_images(session: Session, product_id: int) -> List[ProductImage]:
    """Get all images for a product"""
    statement = select(ProductImage).where(
        ProductImage.product_id == product_id,
        not ProductImage.is_deleted
    ).order_by(ProductImage.position)
    return list(session.exec(statement).all())


def get_product_image_by_id(session: Session, image_id: int) -> Optional[ProductImage]:
    """Get a product image by ID"""
    statement = select(ProductImage).where(
        ProductImage.id == image_id,
        not ProductImage.is_deleted
    )
    return session.exec(statement).first()


def create_product_image(session: Session, image_data: ProductImageCreate) -> ProductImage:
    """Create a new product image"""
    # Verify product exists
    product = get_product_by_id(session, image_data.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    image = ProductImage(**image_data.model_dump())
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


def update_product_image(session: Session, image_id: int, image_data: ProductImageUpdate) -> ProductImage:
    """Update an existing product image"""
    image = get_product_image_by_id(session, image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product image not found"
        )

    update_data = image_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(image, field, value)

    session.add(image)
    session.commit()
    session.refresh(image)
    return image


def delete_product_image(session: Session, image_id: int) -> dict:
    """Soft delete a product image"""
    image = get_product_image_by_id(session, image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product image not found"
        )

    image.is_deleted = True
    session.add(image)
    session.commit()
    return {"message": "Product image deleted successfully"}
