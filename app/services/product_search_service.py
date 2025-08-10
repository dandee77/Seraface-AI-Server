"""
Product Search Service

Handles product searching via SerpAPI and database caching.
Based on serpapi_immersive.py logic with MongoDB integration.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..core.config import settings
from ..core.database import Database


class ProductSearchService:
    """Service for searching and caching product data"""
    
    def __init__(self):
        self.api_key = settings.SERPAPI_KEY
        self.products_cache_collection = "products_cache"  # Existing cache
        self.user_products_collection = "user_recommended_products"  # New collection
    
    def _get_database(self) -> AsyncIOMotorDatabase:
        """Get MongoDB database instance"""
        return Database.get_database()
    
    async def search_product_in_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """Search for product in existing cache by query"""
        try:
            db = self._get_database()
            collection = db[self.products_cache_collection]
            
            # Search by query (case-insensitive)
            query_key = query.lower().strip()
            product = await collection.find_one({"query": {"$regex": query_key, "$options": "i"}})
            
            if product:
                print(f"✅ Found '{query}' in cache")
                return product
            
            return None
            
        except Exception as e:
            print(f"❌ Error searching cache for '{query}': {e}")
            return None
    
    def _clean_product_query(self, query: str) -> str:
        """Clean product query for better SerpAPI results"""
        import re
        
        # Remove parenthetical notes and instructions
        cleaned = re.sub(r'\s*\([^)]*\)', '', query)
        
        # Remove common skincare instructions that might confuse search
        instructions_to_remove = [
            "patch test only",
            "use sparingly", 
            "for sensitive skin",
            "apply at night",
            "morning use only",
            "evening use only"
        ]
        
        for instruction in instructions_to_remove:
            cleaned = cleaned.replace(instruction, '')
        
        # Clean up extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned

    async def fetch_product_from_serpapi(self, query: str) -> Optional[Dict[str, Any]]:
        """Fetch product data from SerpAPI using Google Shopping with detailed descriptions"""
        try:
            # Clean up query
            cleaned_query = self._clean_product_query(query)
            
            # Use Google Shopping engine with Philippine locale for PHP prices
            search_params = {
                "engine": "google_shopping",
                "q": cleaned_query,
                "api_key": self.api_key,
                "hl": "en",  # Language: English
                "gl": "ph"   # Country: Philippines (for PHP prices)
            }
            
            search_res = requests.get("https://serpapi.com/search.json", params=search_params)
            
            if search_res.status_code != 200:
                print(f"❌ SerpAPI request failed for '{query}'")
                return None
                
            data = search_res.json()
            
            # Check for errors in response
            if "error" in data:
                print(f"❌ SerpAPI Error for '{query}': {data['error']}")
                return None
            
            # Extract from shopping_results
            shopping_results = data.get("shopping_results", [])
            if not shopping_results:
                print(f"❌ No shopping results found for '{query}'")
                return None
                
            first_result = shopping_results[0]
            
            # Start with basic product data
            product_data = {
                "query": query,
                "title": first_result.get("title"),
                "price": first_result.get("price"),
                "thumbnail": first_result.get("thumbnail"),
                "rating": first_result.get("rating"),
                "reviews": first_result.get("reviews"),
                "source": "shopping_results",
                "fetched_at": datetime.now().isoformat(),
                "position": first_result.get("position"),
                "product_id": first_result.get("product_id"),
                "delivery": first_result.get("delivery"),
                "store": first_result.get("source") or first_result.get("merchant"),
                "product_link": first_result.get("product_link") or first_result.get("link"),
                "extracted_price": first_result.get("extracted_price"),
                "basic_snippet": first_result.get("snippet", ""),
            }
            
            # Try to get detailed product description from product API
            product_api_url = first_result.get("serpapi_product_api")
            detailed_description = ""
            
            if product_api_url:
                try:
                    # Parse and prepare product API parameters
                    parsed_url = urlparse(product_api_url)
                    product_params = parse_qs(parsed_url.query)
                    product_params = {k: v[0] for k, v in product_params.items()}
                    product_params["api_key"] = self.api_key
                    
                    # Fetch detailed product data
                    product_res = requests.get("https://serpapi.com/search.json", params=product_params)
                    
                    if product_res.status_code == 200:
                        product_detail_data = product_res.json()
                        
                        # Extract detailed information
                        product_results = product_detail_data.get("product_results", {})
                        
                        # Get the full description
                        detailed_description = (
                            product_results.get("description") or 
                            product_results.get("about_this_item") or
                            product_results.get("product_description") or
                            ""
                        )
                        
                        # Add more detailed information if available
                        if product_results:
                            product_data.update({
                                "detailed_description": detailed_description,
                                "highlights": product_results.get("highlights", []),
                                "specifications": product_results.get("specifications", {}),
                                "about_this_item": product_results.get("about_this_item"),
                                "ingredients": product_results.get("ingredients"),
                                "directions": product_results.get("directions"),
                                "warnings": product_results.get("warnings"),
                                "detailed_rating": product_results.get("rating"),
                                "detailed_reviews": product_results.get("reviews"),
                                "media": product_results.get("media", []),
                                "variants": product_results.get("variants", []),
                                "seller_info": product_results.get("sellers", []),
                            })
                        
                except Exception as e:
                    # Silently continue if detailed fetch fails
                    pass
            
            # Use the best available description
            final_description = (
                detailed_description or 
                product_data.get("basic_snippet", "") or
                "No description available"
            )
            
            product_data["description"] = final_description
            
            # Clean up None values and empty strings
            product_data = {k: v for k, v in product_data.items() if v is not None and v != "" and v != []}
            
            print(f"✅ Successfully fetched '{query}' from SerpAPI")
            return product_data
            
        except Exception as e:
            print(f"❌ Error fetching '{query}' from SerpAPI: {e}")
            return None
    
    async def save_to_products_cache(self, product_data: Dict[str, Any]) -> bool:
        """Save product data to products cache collection"""
        try:
            db = self._get_database()
            collection = db[self.products_cache_collection]
            
            # Create cache document with unique key
            query_key = product_data["query"].lower().strip()
            cache_document = {
                "_id": query_key,
                "key": query_key,
                **product_data,
                "cached_at": datetime.utcnow()
            }
            
            await collection.replace_one(
                {"_id": query_key}, 
                cache_document, 
                upsert=True
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving to cache: {e}")
            return False
    
    async def save_user_recommended_product(self, session_id: str, product_data: Dict[str, Any], recommendation_context: Dict[str, Any]) -> bool:
        """Save recommended product for specific user session"""
        try:
            db = self._get_database()
            collection = db[self.user_products_collection]
            
            # Create user product document
            user_product_document = {
                "_id": f"{session_id}_{product_data['query'].lower().strip()}",
                "session_id": session_id,
                "product_query": product_data["query"],
                "product_data": product_data,
                "recommendation_context": recommendation_context,
                "recommended_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=365)  # Keep user recommendations longer
            }
            
            await collection.replace_one(
                {"_id": user_product_document["_id"]}, 
                user_product_document, 
                upsert=True
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving user recommended product: {e}")
            return False
    
    async def get_or_fetch_product(self, query: str, session_id: str = None, recommendation_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Get product data from cache or fetch from SerpAPI if not found.
        Optionally save to user recommendations if session_id provided.
        """
        try:
            # Step 1: Try to find in cache
            product_data = await self.search_product_in_cache(query)
            
            # Step 2: If not in cache, fetch from SerpAPI
            if not product_data:
                product_data = await self.fetch_product_from_serpapi(query)
                
                if not product_data:
                    return None
                
                # Save to products cache
                await self.save_to_products_cache(product_data)
            
            # Step 3: If session provided, save to user recommendations
            if session_id and recommendation_context:
                await self.save_user_recommended_product(session_id, product_data, recommendation_context)
            
            return product_data
            
        except Exception as e:
            print(f"❌ Error in get_or_fetch_product for '{query}': {e}")
            return None
    
    async def get_user_recommended_products(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all recommended products for a specific session"""
        try:
            db = self._get_database()
            collection = db[self.user_products_collection]
            
            user_products = []
            async for document in collection.find({"session_id": session_id}):
                user_products.append({
                    "product_query": document["product_query"],
                    "product_data": document["product_data"],
                    "recommendation_context": document["recommendation_context"],
                    "recommended_at": document["recommended_at"]
                })
            
            return user_products
            
        except Exception as e:
            print(f"❌ Error getting user recommended products: {e}")
            return []


product_search_service = ProductSearchService()
