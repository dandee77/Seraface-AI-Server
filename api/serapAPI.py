import json
import os
from datetime import datetime
from serpapi import GoogleSearch

CACHE_FILE = "immersive_product_cache.json"


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def fetch_immersive_products(query):
    cache = load_cache()
    query_key = query.lower().strip()

    if query_key in cache:
        return cache[query_key]

    params = {
        "engine": "google",
        "q": query,
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "api_key": "YOUR_SERPAPI_KEY"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    immersive_products = results.get("immersive_products", [])
    if not immersive_products:
        return []

    simplified = []
    for item in immersive_products:
        simplified.append({
            "title": item.get("title"),
            "price": item.get("price"),
            "image": item.get("thumbnail"),
            "source": item.get("source"),
            "rating": item.get("rating"),
            "reviews": item.get("reviews"),
            "product_id": item.get("product_id"),
            "serpapi_product_api": item.get("serpapi_product_api"),
            "serpapi_link": item.get("serpapi_link"),
            "fetched_at": datetime.utcnow().isoformat()
        })

    cache[query_key] = simplified
    save_cache(cache)
    return simplified



if __name__ == "__main__":
    q = input("Enter product query: ")
    products = fetch_immersive_products(q)

    if not products:
        print("No immersive products found.")
    else:
        for i, p in enumerate(products, 1):
            print(f"\n[{i}] {p['title']}")
            print(f"Price: {p['price']} | Rating: {p['rating']} ⭐ ({p['reviews']} reviews)")
            print(f"Image: {p['image']}")
            print(f"Source: {p['source']}")
            print(f"Link: {p['serpapi_link']}")