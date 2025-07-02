import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv()

API_KEY = os.getenv("SERPAPI_KEY") or "YOUR_SERPAPI_KEY"

def fetch_product_data(query):
    search_params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY,
        "hl": "en",
        "gl": "us"
    }

    search_res = requests.get("https://serpapi.com/search.json", params=search_params)
    data = search_res.json()

    immersive_products = data.get("immersive_products", [])
    if not immersive_products:
        print("❌ No immersive products found.")
        return None

    first_product = immersive_products[0]
    product_api_url = first_product.get("serpapi_product_api")

    if not product_api_url:
        print("❌ No product API URL found.")
        return None


    parsed_url = urlparse(product_api_url)
    product_params = parse_qs(parsed_url.query)
    product_params = {k: v[0] for k, v in product_params.items()}
    product_params["api_key"] = API_KEY  

    product_res = requests.get("https://serpapi.com/search.json", params=product_params)
    product_data = product_res.json()


    extracted = {
        "query": query,
        "fetched_at": product_data.get("search_metadata", {}).get("created_at"),
        "google_product_url": product_data.get("search_metadata", {}).get("google_product_url"),
    }

    product = product_data.get("product_results", {})
    extracted["pruduct_api_url"] = product_api_url
    extracted["title"] = product.get("title")
    extracted["description"] = product.get("description")
    extracted["rating"] = product.get("rating")
    extracted["reviews"] = product.get("reviews")
    extracted["media"] = product.get("media", [])

    prices = product.get("prices", [])
    if prices:
        extracted["price"] = prices[0]

    related = product_data.get("related_products", {}).get("different_brand", [])
    extracted["related_products"] = [
        {
            "title": r.get("title"),
            "link": r.get("link"),
            "thumbnail": r.get("thumbnail"),
            "price": r.get("price"),
            "rating": r.get("rating"),
            "reviews": r.get("reviews"),
        }
        for r in related
    ]

    return extracted

if __name__ == "__main__":
    query = input("Enter your search query: ")
    result = fetch_product_data(query)

    if result:
        print(json.dumps(result, indent=2))

        fname = f"cache_{query.lower().replace(' ', '_')}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            print(f"\n✅ Saved to {fname}")
