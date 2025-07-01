import json
import os
from datetime import datetime
from serpapi import GoogleSearch # shit aint working without the pip `install google-search-results`
# import serpapi # alternative to GoogleSearch
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = "immersive_product_cache.json"
api_key = os.getenv("SERPAPI_KEY")

if not api_key:
    raise RuntimeError("SERPAPI_KEY not found in environment variables")

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
        "q": query,
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "api_key": api_key
    }

    search = GoogleSearch(params)
    # search = serpapi.search(params) # alternative to GoogleSearch
    results = search.get_dict() 

    immersive_products = results.get("immersive_products", [])
    inline_videos = results.get("inline_videos", [])
    perspectives = results.get("perspectives", [])

    simplified_products = []
    for item in immersive_products:
        simplified_products.append({
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

    simplified_videos = []
    for video in inline_videos:
        simplified_videos.append({
            "title": video.get("title"),
            "link": video.get("link"),
            "thumbnail": video.get("thumbnail"),
            "channel": video.get("channel"),
            "duration": video.get("duration"),
            "platform": video.get("platform")
        })

    simplified_perspectives = []
    for perspective in perspectives:
        simplified_perspectives.append({
            "author": perspective.get("author"),
            "source": perspective.get("source"),
            "extensions": perspective.get("extensions"),
            "thumbnails": perspective.get("thumbnails"),
            "title": perspective.get("title"),
            "link": perspective.get("link"),
            "date": perspective.get("date"),
            "video": perspective.get("video")
        })

    result_data = {
        "products": simplified_products,
        "videos": simplified_videos,
        "perspectives": simplified_perspectives,
        "fetched_at": datetime.utcnow().isoformat()
    }

    cache[query_key] = result_data
    save_cache(cache)
    return result_data



q = input("Enter product query: ")
data = fetch_immersive_products(q)

if not data["products"]:
    print("No immersive products found.")
else:
    for i, p in enumerate(data["products"], 1):
        print(f"\n[{i}] {p['title']}")
        print(f"Price: {p['price']} | Rating: {p['rating']} ⭐ ({p['reviews']} reviews)")
        print(f"Image: {p['image']}")
        print(f"Source: {p['source']}")
        print(f"Link: {p['serpapi_link']}")

if data["videos"]:
    print("\nInline Videos:")
    for v in data["videos"]:
        print(f"- {v['title']} ({v['duration']}) - {v['platform']} → {v['link']}")

if data["perspectives"]:
    print("\nPerspectives:")
    for p in data["perspectives"]:
        print(f"- {p['title']} by {p['author']} ({p['source']}) → {p['link']}")
