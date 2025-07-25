from typing import List, Dict, Optional
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: str


class BudgetAllocation(BaseModel):
    facial_wash: Optional[int] = None
    moisturizer: Optional[int] = None
    sunscreen: Optional[int] = None
    treatment: Optional[int] = None
    serum: Optional[int] = None
    exfoliant: Optional[int] = None
    toner: Optional[int] = None
    eye_cream: Optional[int] = None
    mask: Optional[int] = None
    essence: Optional[int] = None
    ampoule: Optional[int] = None


class ProductRecommendations(BaseModel):
    facial_wash: Optional[List[Product]] = None
    moisturizer: Optional[List[Product]] = None
    sunscreen: Optional[List[Product]] = None
    treatment: Optional[List[Product]] = None
    serum: Optional[List[Product]] = None
    exfoliant: Optional[List[Product]] = None
    toner: Optional[List[Product]] = None
    eye_cream: Optional[List[Product]] = None
    mask: Optional[List[Product]] = None
    essence: Optional[List[Product]] = None
    ampoule: Optional[List[Product]] = None


class FutureRecommendation(BaseModel):
    category: str
    products: List[Product]


class ProductRecommendationResponse(BaseModel):
    allocation: Dict[str, int]
    products: Dict[str, List[Product]]
    total_budget: str
    future_recommendations: List[FutureRecommendation]
