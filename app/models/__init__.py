"""
Models Package

Contains all Pydantic models for the Seraface AI Server:
- product_schemas: Product CRUD models
- skincare: AI skincare analysis models
"""

from .product_schemas import (
    ProductCreate,
    ProductResponse,
    ProductBase,
    ProductInDB,
    MediaItem,
    RelatedProduct
)
