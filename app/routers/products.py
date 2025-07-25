from typing import List
from fastapi import APIRouter, HTTPException, status
from ..models import ProductCreate, ProductResponse
from ..services import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=List[ProductResponse])
async def get_all_products():
    """Retrieve all products"""
    try:
        products = await ProductService.get_all_products()
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products: {str(e)}"
        )


@router.get("/{key}", response_model=ProductResponse)
async def get_product_by_key(key: str):
    """Retrieve a product by its key"""
    try:
        product = await ProductService.get_product_by_key(key)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with key '{key}' not found"
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve product: {str(e)}"
        )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate):
    """Create a new product"""
    try:
        # Check if product with this key already exists
        existing_product = await ProductService.get_product_by_key(product.key)
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with key '{product.key}' already exists"
            )
        
        new_product = await ProductService.create_product(product)
        return new_product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


@router.put("/{key}", response_model=ProductResponse)
async def update_product(key: str, product: ProductCreate):
    """Update an existing product"""
    try:
        updated_product = await ProductService.update_product(key, product)
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with key '{key}' not found"
            )
        return updated_product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}"
        )


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(key: str):
    """Delete a product by its key"""
    try:
        deleted = await ProductService.delete_product(key)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with key '{key}' not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}"
        )
