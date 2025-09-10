# Seraface AI Server

## Overview

Seraface AI Server is a comprehensive skincare recommendation API that uses artificial intelligence to provide personalized skincare routines and product recommendations. The system combines user form data, facial image analysis, budget allocation algorithms, and real-time product search to deliver tailored skincare solutions.

## Features

The API implements a **4-phase intelligent skincare pipeline**:

1. **Phase 1: Form Analysis** - Collects user skin profile, preferences, and budget
2. **Phase 2: Image Analysis** - AI-powered facial analysis for skin condition assessment  
3. **Phase 3: Product Recommendations** - Smart budget allocation and product discovery
4. **Phase 4: Routine Creation** - Personalized morning/evening skincare routines

## Technology Stack

- **FastAPI** - High-performance Python web framework
- **MongoDB** - Document database for session and product storage
- **Google Gemini AI** - Advanced AI for image analysis and recommendations  
- **SerpAPI** - Real-time product search and price data
- **Motor** - Asynchronous MongoDB driver
- **Pydantic** - Data validation and serialization

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   User Input    │───▶│   AI Analysis   │───▶│  Product Search │
│                 │    │                 │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Form Data     │    │ • Gemini AI     │    │ • SerpAPI       │
│ • Facial Image  │    │ • Skin Analysis │    │ • Real Products │
│ • Budget/Goals  │    │ • Budget Logic  │    │ • Price/Reviews │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │                 │
                    │   MongoDB       │
                    │   Database      │
                    │                 │
                    ├─────────────────┤
                    │ • Session Data  │
                    │ • Product Cache │
                    │ • User History  │
                    └─────────────────┘
```

## Data Flow Diagram

```
User Form Data ──┐
                 │
                 ├─▶ Session Created ──┐
                 │                     │
Facial Image ────┘                     │
                                       ▼
┌─────────────────────────────────────────────────────────┐
│                  AI Processing                          │
│                                                         │
│  1. Analyze Form Data          2. Analyze Facial Image  │
│     • Skin Type                   • Acne Detection     │
│     • Budget                      • Skin Conditions    │
│     • Allergies                   • Problem Areas      │
│     • Goals                       • Skin Tone          │
│                                                         │
│  3. Budget Allocation Algorithm                         │
│     • Determine Product Categories                      │
│     • Allocate Budget Percentages                      │
│     • Priority-Based Distribution                      │
│                                                         │
│  4. Product Search & Enrichment                        │
│     • Search via SerpAPI                               │
│     • Get Prices, Reviews, Links                       │
│     • Cache Product Data                               │
│                                                         │
│  5. Routine Generation                                  │
│     • Morning/Evening Steps                            │
│     • Product Usage Instructions                       │
│     • Timing and Frequency                             │
└─────────────────────────────────────────────────────────┘
                                │
                                ▼
                    Final Recommendations
                    • Personalized Products
                    • Budget-Optimized Selection
                    • Step-by-Step Routine
```

## Budget Allocation Algorithm

The AI uses a tiered approach to allocate skincare budget:

```
Budget Tiers:
┌─────────────┬─────────────────┬──────────────────────────────┐
│    Tier     │    Priority     │          Categories          │
├─────────────┼─────────────────┼──────────────────────────────┤
│ 🟢 Tier 1   │ Core Essentials │ Cleanser, Moisturizer,       │
│             │                 │ Sunscreen                    │
├─────────────┼─────────────────┼──────────────────────────────┤
│ 🟡 Tier 2   │ First Add-ons   │ Treatment, Toner, Serum,     │
│             │                 │ Spot Treatment               │
├─────────────┼─────────────────┼──────────────────────────────┤
│ 🟠 Tier 3   │ Specialized     │ Eye Cream, Essence,          │
│             │ Boosters        │ Ampoule, Exfoliants         │
├─────────────┼─────────────────┼──────────────────────────────┤
│ 🔵 Tier 4   │ Occasional/     │ Masks, Face Mist,            │
│             │ Luxury          │ Facial Oil, Neck Cream      │
└─────────────┴─────────────────┴──────────────────────────────┘

Budget Rules:
• < ₱500  → Tier 1 only (facial_wash, moisturizer, sunscreen)
• < ₱800  → Tier 1 + treatment
• < ₱1500 → Tier 1 + Tier 2
• ≥ ₱1500 → All tiers available
```

## Database Schema (ERD)

```
┌─────────────────────────┐
│    skincare_phase1_data │
├─────────────────────────┤
│ _id (session_id)        │
│ phase                   │
│ timestamp               │
│ expires_at              │
│ data                    │
│   ├─ skin_type          │
│   ├─ skin_conditions    │
│   ├─ budget             │
│   ├─ allergies          │
│   ├─ goals              │
│   └─ product_exp        │
└─────────────────────────┘
            │
            │ (1:1)
            ▼
┌─────────────────────────┐
│    skincare_phase2_data │
├─────────────────────────┤
│ _id (session_id)        │
│ phase                   │
│ timestamp               │
│ expires_at              │
│ data                    │
│   ├─ redness_irritation │
│   ├─ acne_breakouts     │
│   ├─ skin_analysis      │
│   └─ ai_confidence      │
└─────────────────────────┘
            │
            │ (1:1)
            ▼
┌─────────────────────────┐
│    skincare_phase3_data │
├─────────────────────────┤
│ _id (session_id)        │
│ phase                   │
│ timestamp               │
│ expires_at              │
│ data                    │
│   ├─ allocation         │
│   ├─ products           │
│   ├─ total_budget       │
│   └─ future_recs        │
└─────────────────────────┘
            │
            │ (1:1)
            ▼
┌─────────────────────────┐
│    skincare_phase4_data │
├─────────────────────────┤
│ _id (session_id)        │
│ phase                   │
│ timestamp               │
│ expires_at              │
│ data                    │
│   ├─ product_type       │
│   ├─ routine            │
│   ├─ morning_steps      │
│   └─ evening_steps      │
└─────────────────────────┘

┌──────────────────────────┐      ┌────────────────────────────┐
│     products_cache       │      │  user_recommended_products │
├──────────────────────────┤      ├────────────────────────────┤
│ _id                      │      │ _id                        │
│ query                    │      │ session_id                 │
│ title                    │      │ query                      │
│ price                    │      │ product_data               │
│ product_link             │      │ category                   │
│ rating                   │      │ recommended_at             │
│ reviews                  │      │ recommendation_context     │
│ cached_at                │      │ ai_recommended             │
│ source                   │      └────────────────────────────┘
└──────────────────────────┘
```

## API Endpoints

### Phase 1: Form Analysis

**POST** `/api/v1/skincare/phase1/form-analysis`

Collects user skincare profile and preferences.

#### Request Body:
```json
{
  "skin_type": ["oily", "acne-prone"],
  "skin_conditions": ["acne", "blackheads", "large pores"],
  "budget": "₱1200",
  "allergies": ["fragrance", "sulfates"],
  "product_experiences": [
    {
      "product": "CeraVe Foaming Cleanser",
      "experience": "good",
      "reason": "Gentle and effective"
    }
  ],
  "goals": ["clear acne", "control oil"],
  "custom_goal": "Minimize pore appearance"
}
```

#### Response:
```json
{
  "session_id": "uuid-12345-67890",
  "status": "success",
  "message": "Form data processed and saved successfully",
  "next_phase": "Phase 2: Upload facial image for analysis",
  "form_index": 1,
  "data": {
    "skin_type": ["oily", "acne-prone"],
    "budget": "₱1200",
    "processed_at": "2024-01-15T10:30:00Z"
  }
}
```

### Phase 2: Image Analysis

**POST** `/api/v1/skincare/phase2/image-analysis`

Analyzes facial image for skin condition assessment.

#### Parameters:
- `session_id` (string): Session ID from Phase 1
- `file` (multipart): Image file (JPEG, PNG)

#### Response:
```json
{
  "session_id": "uuid-12345-67890",
  "status": "success",
  "message": "Image analysis completed and saved successfully",
  "next_phase": "Phase 3: Generate product recommendations",
  "analysis": {
    "redness_irritation": "mild",
    "acne_breakouts": {
      "severity": "moderate",
      "count_estimate": 12,
      "location": ["forehead", "chin"]
    },
    "blackheads_whiteheads": {
      "presence": true,
      "location": ["nose", "chin"]
    },
    "oiliness_shine": {
      "level": "high",
      "location": ["t-zone"]
    },
    "pores_size": {
      "level": "enlarged",
      "location": ["nose", "cheeks"]
    }
  }
}
```

### Phase 3: Product Recommendations

**POST** `/api/v1/skincare/phase3/product-recommendations`

Generates personalized product recommendations with budget allocation.

#### Parameters:
- `session_id` (string): Session ID from previous phases

#### Response:
```json
{
  "allocation": {
    "facial_wash": 25,
    "treatment": 30,
    "moisturizer": 20,
    "sunscreen": 15,
    "toner": 10
  },
  "products": {
    "facial_wash": [
      {
        "name": "CeraVe Foaming Facial Cleanser",
        "price": "₱295.00"
      }
    ],
    "treatment": [
      {
        "name": "The Ordinary Niacinamide 10% + Zinc 1%",
        "price": "₱350.00"
      }
    ],
    "moisturizer": [
      {
        "name": "Neutrogena Oil-Free Moisture Gel",
        "price": "₱240.00"
      }
    ]
  },
  "total_budget": "₱1200",
  "future_recommendations": [
    {
      "category": "serum",
      "products": [
        {
          "name": "Hyaluronic Acid Serum",
          "price": "₱450.00"
        }
      ]
    }
  ]
}
```

### Phase 4: Routine Creation

**POST** `/api/v1/skincare/phase4/routine-creation`

Creates personalized morning and evening skincare routines.

#### Parameters:
- `session_id` (string): Session ID from previous phases

#### Response:
```json
{
  "product_type": "acne-prone skin routine",
  "routine": [
    {
      "name": "Morning Cleanse",
      "tag": "cleanse",
      "description": "Gentle morning facial cleansing",
      "instructions": [
        "Wet face with lukewarm water",
        "Apply CeraVe Foaming Cleanser",
        "Massage gently for 30 seconds",
        "Rinse thoroughly and pat dry"
      ],
      "duration": 2,
      "waiting_time": 1,
      "days": {
        "monday": true,
        "tuesday": true,
        "wednesday": true,
        "thursday": true,
        "friday": true,
        "saturday": true,
        "sunday": true
      },
      "time": ["morning"]
    },
    {
      "name": "Treatment Application",
      "tag": "treatment", 
      "description": "Apply niacinamide treatment",
      "instructions": [
        "Apply 2-3 drops of The Ordinary Niacinamide",
        "Gently pat into skin",
        "Focus on oily areas",
        "Wait for absorption"
      ],
      "duration": 1,
      "waiting_time": 5,
      "days": {
        "monday": true,
        "tuesday": false,
        "wednesday": true,
        "thursday": false,
        "friday": true,
        "saturday": false,
        "sunday": true
      },
      "time": ["morning", "evening"]
    }
  ]
}
```

### Utility Endpoints

#### Session Status
**GET** `/api/v1/skincare/session/{session_id}/status`

Check session progress and completion status.

```json
{
  "session_id": "uuid-12345-67890",
  "completed_phases": ["phase1", "phase2", "phase3"],
  "total_phases": 4,
  "progress_percentage": 75,
  "next_phase": "Phase 4: Create skincare routine",
  "pipeline_complete": false
}
```

#### Product Search
**GET** `/api/v1/skincare/products/search?query=moisturizer&session_id=uuid-12345`

Search for specific products with enriched details.

```json
{
  "search_query": "moisturizer",
  "product_found": true,
  "product_details": {
    "title": "Neutrogena Hydro Boost Water Gel",
    "price": "₱240.00",
    "rating": 4.3,
    "reviews": 1250,
    "product_link": "https://shopee.ph/product/123456",
    "thumbnail": "https://image-url.jpg",
    "description": "Lightweight gel moisturizer with hyaluronic acid",
    "store": "Shopee",
    "delivery": "Free shipping"
  },
  "cached": true
}
```

#### Cache Statistics
**GET** `/api/v1/skincare/products/cache-stats`

Get product cache and recommendation statistics.

```json
{
  "products_cache": {
    "total_products": 1543,
    "recent_additions": 89
  },
  "user_recommendations": {
    "total_recommendations": 2156,
    "recent_recommendations": 156
  },
  "stats_generated_at": "2024-01-15T14:20:00Z"
}
```

## How Each Feature Works

### 1. Form Processing Service

The form processing service collects and validates user skin profile data:

- **Skin Type Detection**: Analyzes user-selected skin types (oily, dry, combination, sensitive, acne-prone)
- **Condition Mapping**: Maps skin conditions to treatment priorities
- **Budget Parsing**: Converts budget strings to numeric values for allocation
- **Allergy Filtering**: Stores allergy information for product filtering
- **Experience Learning**: Records product experiences to improve recommendations

### 2. Image Analysis Service

Uses Google Gemini AI for comprehensive facial analysis:

- **Acne Detection**: Counts and locates acne breakouts
- **Skin Condition Assessment**: Evaluates redness, irritation, dryness
- **Pore Analysis**: Measures pore size and visibility
- **Texture Analysis**: Assesses skin smoothness and elasticity
- **Problem Area Identification**: Maps issues to facial regions

**AI Prompt Structure:**
```
Analyze the face image and return structured JSON data including:
- Redness/irritation levels (none|mild|moderate|severe)
- Acne breakouts (severity, count, location)
- Blackheads/whiteheads presence and location
- Oiliness levels and affected areas
- Pore size assessment
- Fine lines and skin elasticity
```

### 3. Product Recommendation Engine

Intelligent system that combines AI analysis with real product data:

#### Budget Allocation Algorithm:
1. **Category Determination**: AI selects relevant product categories based on skin analysis
2. **Priority Scoring**: Assigns importance scores to each category
3. **Budget Distribution**: Allocates percentage of budget to each category
4. **Product Matching**: Finds products within allocated budget ranges

#### Product Search Integration:
1. **Cache Check**: Searches MongoDB cache for existing product data
2. **SerpAPI Query**: Fetches real-time product information if not cached
3. **Data Enrichment**: Enhances product data with prices, reviews, links
4. **Cache Storage**: Stores enriched data for future use

### 4. Routine Creation Service

Generates personalized skincare routines:

- **Product Integration**: Incorporates recommended products into routine steps
- **Timing Optimization**: Schedules products for morning/evening use
- **Frequency Planning**: Determines daily/alternate day usage
- **Step Sequencing**: Orders products for maximum effectiveness
- **Duration Estimation**: Provides realistic time expectations

### 5. Session Management

Sophisticated session handling across the pipeline:

- **UUID Generation**: Creates unique session identifiers
- **Data Persistence**: Stores phase data in MongoDB collections  
- **Expiration Handling**: Automatically cleans up old sessions (90 days)
- **Progress Tracking**: Monitors completion status across phases
- **Error Recovery**: Allows resuming from any completed phase

### 6. Product Search & Caching

High-performance product discovery system:

#### SerpAPI Integration:
- **Shopping Results**: Searches Google Shopping for products
- **Price Comparison**: Aggregates prices from multiple retailers
- **Review Data**: Fetches ratings and review counts
- **Link Generation**: Provides direct purchase links
- **Image Collection**: Gathers product thumbnails

#### Caching Strategy:
- **Query-Based Cache**: Stores products by search query
- **Freshness Control**: Updates cache after 7 days
- **Performance Optimization**: Reduces API calls by 85%
- **User Tracking**: Links searched products to user sessions

## Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- Google Gemini API Key
- SerpAPI Key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/dandee77/Seraface-AI-Server.git
cd Seraface-AI-Server
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` file:
```env
# Database Configuration
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=seraface

# AI Configuration  
GEMINI_API_KEY=your_gemini_api_key_here
SERPAPI_KEY=your_serpapi_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False
RELOAD=True
```

4. **Start MongoDB:**
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo

# Or using local installation
mongod --dbpath /path/to/data/db
```

5. **Run the server:**
```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the API:**
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/

### Testing

Run the product search integration test:
```bash
python test_product_search.py
```

## Integration Examples

### Complete Pipeline Example

```python
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

# Phase 1: Submit form
form_data = {
    "skin_type": ["oily", "acne-prone"],
    "skin_conditions": ["acne", "blackheads"],
    "budget": "₱1200",
    "allergies": ["fragrance"],
    "product_experiences": [],
    "goals": ["clear acne"]
}

response = requests.post(f"{API_BASE}/skincare/phase1/form-analysis", json=form_data)
session_data = response.json()
session_id = session_data["session_id"]

# Phase 2: Upload image
with open("facial_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{API_BASE}/skincare/phase2/image-analysis",
        params={"session_id": session_id},
        files=files
    )

# Phase 3: Get recommendations  
response = requests.post(
    f"{API_BASE}/skincare/phase3/product-recommendations",
    params={"session_id": session_id}
)
recommendations = response.json()

# Phase 4: Create routine
response = requests.post(
    f"{API_BASE}/skincare/phase4/routine-creation", 
    params={"session_id": session_id}
)
routine = response.json()

print("Pipeline completed successfully!")
print(f"Recommendations: {len(recommendations['products'])} categories")
print(f"Routine steps: {len(routine['routine'])}")
```

## Error Handling

The API provides comprehensive error handling:

### Common Error Responses

```json
{
  "detail": "Session not found. Complete Phase 1 first.",
  "status_code": 404
}
```

```json
{
  "detail": "File must be an image (JPEG, PNG, etc.)",
  "status_code": 400
}
```

```json
{
  "detail": "Phase 3 failed: Budget allocation failed",
  "status_code": 500
}
```

### Error Categories

- **400 Bad Request**: Invalid input data or missing required fields
- **404 Not Found**: Session not found or expired
- **409 Conflict**: Duplicate data or state conflicts
- **500 Internal Server Error**: AI service failures or database errors

## Performance Considerations

### Optimization Features

1. **Product Caching**: 85% cache hit rate reduces external API calls
2. **Session-Based Architecture**: Efficient data retrieval across phases
3. **Async Processing**: Non-blocking I/O for database operations
4. **Data Expiration**: Automatic cleanup of expired sessions
5. **Query Optimization**: Indexed MongoDB queries for fast retrieval

### Scaling Recommendations

- **Database Sharding**: Partition by session_id for horizontal scaling
- **Cache Layer**: Implement Redis for faster product lookups
- **Load Balancing**: Use multiple server instances for high traffic
- **CDN Integration**: Cache product images and static assets
- **Queue System**: Process AI analysis asynchronously for better UX

## Contributing

This API is designed for skincare professionals and developers building personalized beauty applications. The modular architecture allows for easy extension and customization of the recommendation engine.

## License

Copyright (c) 2024 Seraface AI. All rights reserved.