from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MediaItem(BaseModel):
    type: str
    link: str  # Changed from HttpUrl to str for MongoDB compatibility


class RelatedProduct(BaseModel):
    title: str
    link: str  # Changed from HttpUrl to str for MongoDB compatibility
    thumbnail: str  # Changed from HttpUrl to str for MongoDB compatibility
    price: str
    rating: Optional[float] = None
    reviews: Optional[int] = None


class ProductBase(BaseModel):
    query: str
    fetched_at: str
    google_product_url: Optional[str] = None  
    product_api_url: Optional[str] = None  
    title: str
    description: str
    rating: Optional[float] = None
    reviews: Optional[int] = None
    media: List[MediaItem] = Field(default_factory=list)
    price: str
    related_products: List[RelatedProduct] = Field(default_factory=list)


class ProductCreate(ProductBase):
    key: str


class ProductInDB(ProductBase):
    id: str = Field(alias="_id")
    key: str

    class Config:
        populate_by_name = True  # Updated for Pydantic v2


class ProductResponse(ProductBase):
    id: str
    key: str

    class Config:
        from_attributes = True  # Updated for Pydantic v2
