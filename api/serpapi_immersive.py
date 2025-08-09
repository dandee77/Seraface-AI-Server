import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv()

API_KEY = os.getenv("SERPAPI_KEY") or "YOUR_SERPAPI_KEY"
CACHE_FILE = "products_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache_data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)

def clean_product_query(query):
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

def fetch_product_data(query):
    cache = load_cache()
    query_key = query.lower().strip()

    if query_key in cache:
        print("✅ Found in cache.")
        return cache[query_key]

    print("🔍 Not found in cache. Fetching from SerpAPI...")

    # Clean up query
    cleaned_query = clean_product_query(query)
    print(f"🧹 Cleaned query: '{cleaned_query}'")

    # Use Google Shopping engine for consistent results
    print("🛒 Searching with Google Shopping engine...")
    shopping_params = {
        "engine": "google_shopping",
        "q": cleaned_query,
        "api_key": API_KEY,
        "hl": "en",
        "gl": "us"
    }

    print(f"🌐 Calling SerpAPI with params: {shopping_params}")
    shopping_res = requests.get("https://serpapi.com/search.json", params=shopping_params)
    
    if shopping_res.status_code != 200:
        print(f"❌ SerpAPI request failed with status {shopping_res.status_code}")
        print(f"❌ Response: {shopping_res.text}")
        return None
        
    shopping_data = shopping_res.json()
    
    # Check for errors
    if "error" in shopping_data:
        print(f"❌ SerpAPI Error: {shopping_data['error']}")
        return None
    
    print(f"📊 Response keys: {list(shopping_data.keys())}")
    
    # Extract from shopping_results
    shopping_results = shopping_data.get("shopping_results", [])
    if not shopping_results:
        print("❌ No shopping results found.")
        return None
        
    print(f"🛒 Found {len(shopping_results)} shopping results, using first one...")
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
        print("🔍 Found product API URL, fetching detailed information...")
        try:
            # Parse and prepare product API parameters
            parsed_url = urlparse(product_api_url)
            product_params = parse_qs(parsed_url.query)
            product_params = {k: v[0] for k, v in product_params.items()}
            product_params["api_key"] = API_KEY
            
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
                    
                print("✅ Successfully fetched detailed product information")
            else:
                print(f"⚠️  Product API request failed with status {product_res.status_code}")
                
        except Exception as e:
            print(f"⚠️  Error fetching detailed product info: {e}")
    
    # Use the best available description
    final_description = (
        detailed_description or 
        product_data.get("basic_snippet", "") or
        "No description available"
    )
    
    product_data["description"] = final_description
    
    # Clean up None values and empty strings
    product_data = {k: v for k, v in product_data.items() if v is not None and v != "" and v != []}
    
    print(f"📦 Extracted fields: {list(product_data.keys())}")
    
    # Show key product info
    print(f"🏷️  Product: {product_data.get('title', 'N/A')}")
    print(f"💰 Price: {product_data.get('price', 'N/A')}")
    print(f"🔗 Link: {product_data.get('product_link', 'N/A')}")
    print(f"📝 Description: {final_description[:200]}...")
    print(f"🏪 Store: {product_data.get('store', 'N/A')}")
    print(f"⭐ Rating: {product_data.get('rating', 'N/A')} ({product_data.get('reviews', 'N/A')} reviews)")
    
    # Cache and return
    cache[query_key] = product_data
    save_cache(cache)
    print("✅ Fetched and cached from shopping results.")
    return product_data


# TODO: PASS THE FUNCTION LATER
query = input("Enter your search query: ")
result = fetch_product_data(query)

if result:
    print(json.dumps(result, indent=2))
