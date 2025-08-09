"""
Test Script: Product Search Integration

Test the new product search and database integration functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to path
sys.path.append(str(Path(__file__).parent))

from app.core.database import Database
from app.services.product_search_service import product_search_service


async def test_product_search():
    """Test the product search functionality"""
    
    print("🧪 Testing Product Search Integration")
    print("="*50)
    
    # Connect to database
    Database.connect()
    
    # Test product search
    test_products = [
        "CeraVe Foaming Facial Cleanser",
        "Neutrogena Hydro Boost Water Gel",
        "La Roche-Posay Anthelios Sunscreen"
    ]
    
    session_id = "test-session-123"
    
    for product_name in test_products:
        print(f"\n🔍 Testing search for: {product_name}")
        
        context = {
            "category": "test",
            "recommended_price": "$25.00",
            "user_context": {"test": True},
            "ai_recommended": True
        }
        
        try:
            result = await product_search_service.get_or_fetch_product(
                query=product_name,
                session_id=session_id,
                recommendation_context=context
            )
            
            if result:
                print(f"✅ Found product: {result.get('title', 'N/A')}")
                print(f"   Price: {result.get('price', 'N/A')}")
                print(f"   Rating: {result.get('rating', 'N/A')}")
            else:
                print(f"❌ Product not found: {product_name}")
                
        except Exception as e:
            print(f"❌ Error searching for {product_name}: {e}")
    
    # Test user recommended products retrieval
    print(f"\n📋 Testing user recommended products for session: {session_id}")
    try:
        user_products = await product_search_service.get_user_recommended_products(session_id)
        print(f"✅ Found {len(user_products)} recommended products for session")
        
        for i, product in enumerate(user_products, 1):
            print(f"   {i}. {product['product_query']} (Category: {product['recommendation_context']['category']})")
            
    except Exception as e:
        print(f"❌ Error getting user products: {e}")
    
    # Close database connection
    Database.disconnect()
    print("\n🎉 Test completed!")


if __name__ == "__main__":
    asyncio.run(test_product_search())
