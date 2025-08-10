from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel


class Product(BaseModel):
    """Simple product model for API responses"""
    name: str
    price: str


class EnrichedProduct(BaseModel):
    """Enhanced product model with comprehensive SerpAPI data"""
    query: str
    title: Optional[str] = None
    price: Optional[str] = None
    product_link: Optional[str] = None  # Main product link
    thumbnail: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    source: Optional[str] = None
    fetched_at: Optional[str] = None
    position: Optional[int] = None
    product_id: Optional[str] = None
    delivery: Optional[str] = None
    store: Optional[str] = None
    extracted_price: Optional[float] = None
    
    # Enhanced description fields
    description: Optional[str] = None  # Best available description
    detailed_description: Optional[str] = None  # Full product description
    basic_snippet: Optional[str] = None  # Short snippet from search
    about_this_item: Optional[str] = None
    
    # Additional product details
    highlights: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None
    ingredients: Optional[str] = None
    directions: Optional[str] = None
    warnings: Optional[str] = None
    
    # Enhanced rating/review data
    detailed_rating: Optional[float] = None
    detailed_reviews: Optional[int] = None
    
    # Media and variants
    media: Optional[List[Dict[str, Any]]] = None
    variants: Optional[List[Dict[str, Any]]] = None
    seller_info: Optional[List[Dict[str, Any]]] = None
    
    # For compatibility with AI recommendations
    @property
    def name(self) -> str:
        """Return title as name for backward compatibility"""
        return self.title or self.query
    
    @property
    def link(self) -> Optional[str]:
        """Return product_link as link for backward compatibility"""
        return self.product_link
    
    def to_simple_product(self) -> Product:
        """Convert to simple Product model for API responses"""
        return Product(
            name=self.title or self.query,
            price=self.price or "₱0.00"
        )


class ProductSearchResult(BaseModel):
    """Container for AI recommendation + SerpAPI enrichment"""
    ai_recommendation: Product
    product_details: Optional[EnrichedProduct] = None
    category: str
    search_successful: bool
    enriched_at: Optional[str] = None
    error: Optional[str] = None


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


class EnrichedFutureRecommendation(BaseModel):
    """Enhanced future recommendation with product search results"""
    category: str
    products: List[ProductSearchResult]


class ProductRecommendationResponse(BaseModel):
    """Standard API response format"""
    allocation: Dict[str, int]
    products: Dict[str, List[Product]]
    total_budget: str
    future_recommendations: List[FutureRecommendation]


class EnrichedProductRecommendationResponse(BaseModel):
    """Internal format with enriched product data"""
    allocation: Dict[str, int]
    products: Dict[str, List[ProductSearchResult]]
    total_budget: str
    future_recommendations: List[EnrichedFutureRecommendation]
    enrichment_summary: Dict[str, Union[str, int, bool]]


class CacheStats(BaseModel):
    """Cache statistics response"""
    total_cached_products: int
    cache_hit_rate: Optional[float] = None
    most_searched_products: List[Dict[str, Union[str, int]]]


class UserRecommendedProductsResponse(BaseModel):
    """User's recommended products response"""
    session_id: str
    total_products: int
    products: List[Dict[str, Any]]  # Flexible structure for product data
