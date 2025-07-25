from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class MediaItem(BaseModel):
    type: str
    link: str  


class RelatedProduct(BaseModel):
    title: str
    link: str  
    thumbnail: str  
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
        allow_population_by_field_name = True


class ProductResponse(ProductBase):
    id: str
    key: str

    class Config:
        from_attributes = True  
