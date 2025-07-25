from typing import List, Optional
from bson import ObjectId
from ..core import Database
from ..models import ProductCreate, ProductResponse


class ProductService:
    @staticmethod
    def _product_helper(product: dict) -> dict:
        """Convert MongoDB document to response format"""
        if not product:
            return None
        
        return {
            "id": str(product["_id"]),
            "key": product["key"],
            "query": product["query"],
            "fetched_at": product["fetched_at"],
            "google_product_url": product.get("google_product_url"),
            "product_api_url": product.get("product_api_url"),
            "title": product["title"],
            "description": product["description"],
            "rating": product.get("rating"),
            "reviews": product.get("reviews"),
            "media": product.get("media", []),
            "price": product["price"],
            "related_products": product.get("related_products", [])
        }
    
    @staticmethod
    async def get_all_products() -> List[ProductResponse]:
        """Retrieve all products from the database"""
        collection = Database.get_products_collection()
        products = []
        
        async for product in collection.find():
            product_data = ProductService._product_helper(product)
            if product_data:
                products.append(ProductResponse(**product_data))
        
        return products
    
    @staticmethod
    async def get_product_by_key(key: str) -> Optional[ProductResponse]:
        """Retrieve a product by its key"""
        collection = Database.get_products_collection()
        product = await collection.find_one({"key": key})
        
        if not product:
            return None
        
        product_data = ProductService._product_helper(product)
        return ProductResponse(**product_data)
    
    @staticmethod
    async def create_product(product_data: ProductCreate) -> ProductResponse:
        """Create a new product in the database"""
        collection = Database.get_products_collection()
        
        # Convert Pydantic model to dict for MongoDB
        product_dict = product_data.model_dump()
        
        # Insert the product
        result = await collection.insert_one(product_dict)
        
        # Fetch the created product
        new_product = await collection.find_one({"_id": result.inserted_id})
        product_response_data = ProductService._product_helper(new_product)
        
        return ProductResponse(**product_response_data)
    
    @staticmethod
    async def update_product(key: str, product_data: ProductCreate) -> Optional[ProductResponse]:
        """Update an existing product"""
        collection = Database.get_products_collection()
        
        product_dict = product_data.model_dump()
        
        result = await collection.update_one(
            {"key": key},
            {"$set": product_dict}
        )
        
        if result.matched_count == 0:
            return None
        
        updated_product = await collection.find_one({"key": key})
        product_response_data = ProductService._product_helper(updated_product)
        
        return ProductResponse(**product_response_data)
    
    @staticmethod
    async def delete_product(key: str) -> bool:
        """Delete a product by its key"""
        collection = Database.get_products_collection()
        
        result = await collection.delete_one({"key": key})
        return result.deleted_count > 0
