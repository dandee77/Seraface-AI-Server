"""
Phase 3 Service: Product Recommendation and Budget Distribution

Generates personalized product recommendations based on form data and image analysis.
Integrates with SerpAPI for product search and MongoDB for storage.
PRESERVED ORIGINAL LOGIC - Added product search integration.
"""

import json
import google.generativeai as genai
from fastapi import HTTPException
from typing import List, Dict, Any
from ..core.config import settings
from ..models.skincare.form_schemas import FormData, ProductExperience
from .product_search_service import product_search_service

genai.configure(api_key=settings.GEMINI_API_KEY)


class Phase3Service:
    """Service for Phase 3: Product Recommendation (Original logic preserved)"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def get_budget_allocation(self, form_data: FormData) -> Dict[str, int]:
        """
        Generates a budget allocation based on user profile and skincare concerns.
        The budget is divided into four tiers based on the user's total budget:
        Tier	     Priority	                    Description
        🟢 Tier 1	Core Essentials	                Cleanser, Moisturizer, Sunscreen
        🟡 Tier 2	First Add-ons	                Treatment, Toner, Serum, Spot Treatment
        🟠 Tier 3	Specialized Boosters	        Eye Cream, Essence, Ampoule, Exfoliants
        🔵 Tier 4	Occasional / Luxury	            Masks, Face Mist, Facial Oil, Neck Cream, Lip Care
        """
        budget_amount = float(form_data.budget.replace("$", "").strip())
        
        if budget_amount < 15:
            allowed_categories = ["facial_wash", "moisturizer", "sunscreen"]
        elif budget_amount < 30:
            allowed_categories = ["facial_wash", "moisturizer", "sunscreen", "treatment"]
        elif budget_amount < 60:
            allowed_categories = ["facial_wash", "moisturizer", "sunscreen", "treatment", "toner", "serum"]
        else:
            allowed_categories = [
                "facial_wash", "moisturizer", "sunscreen", "treatment", "toner",
                "serum", "eye_cream", "exfoliant", "mask", "essence", "ampoule"
            ]

        categories_str = ", ".join(allowed_categories)

        prompt = f"""
You are a skincare budget planning assistant. Based on the user's profile and skincare concerns, allocate their total skincare budget into percentage per product category.

Only use from the following allowed categories (based on budget): {categories_str}

User Profile:
- Skin Type: {', '.join(form_data.skin_type)}
- Skin Conditions: {', '.join(form_data.skin_conditions)}
- Allergies: {', '.join(form_data.allergies)}
- Product Experiences: {[f"{p.product} ({p.experience})" for p in form_data.product_experiences]}
- Goals: {', '.join(form_data.goals + ([form_data.custom_goal] if form_data.custom_goal else []))}
- Budget: {form_data.budget}

Instructions:
- Output a valid JSON object with keys as category names (e.g., facial_wash, moisturizer, sunscreen).
- The values must be raw numbers (not strings), and they must sum up to 100.
- Do NOT include notes, explanations, or markdown — return pure JSON only.
"""

        try:
            response = self.model.generate_content(prompt)
            raw = getattr(response, 'text', '').strip()

            print("🧪 Raw Budget Response:\n", raw)

            if raw.startswith("```"):
                raw = raw.strip("`").strip()
                if raw.startswith("json"):
                    raw = raw[4:].strip()

            parsed = json.loads(raw)
            print("💰 Budget Allocation:", parsed)
            return parsed

        except Exception as e:
            print("❌ Failed to parse budget allocation:", e)
            raise HTTPException(status_code=500, detail="Failed to allocate budget")

    def get_product_recommendations(self, category: str, budget: float, form_data: FormData, skin_analysis=None) -> List[Dict[str, Any]]:
        """Get product recommendations - ORIGINAL LOGIC PRESERVED"""

        analysis_context = ""
        if skin_analysis:
            analysis_context = f"""
Skin Analysis Results:
- Redness/Irritation: {getattr(skin_analysis, 'redness_irritation', 'N/A')}
- Acne Breakouts: {getattr(skin_analysis, 'acne_breakouts', 'N/A')}
- Oiliness/Shine: {getattr(skin_analysis, 'oiliness_shine', 'N/A')}
- Dryness/Flaking: {getattr(skin_analysis, 'dryness_flaking', 'N/A')}
- Uneven Skin Tone: {getattr(skin_analysis, 'uneven_skin_tone', 'N/A')}
- Dark Spots/Scars: {getattr(skin_analysis, 'dark_spots_scars', 'N/A')}
- Pore Size: {getattr(skin_analysis, 'pores_size', 'N/A')}
"""

        prompt = f"""
You are a skincare product recommendation expert. Based on the user's profile and budget, recommend specific {category} products.

User Profile:
- Skin Type: {', '.join(form_data.skin_type)}
- Skin Conditions: {', '.join(form_data.skin_conditions)}
- Allergies: {', '.join(form_data.allergies)}
- Goals: {', '.join(form_data.goals + ([form_data.custom_goal] if form_data.custom_goal else []))}
- Budget for {category}: ${budget}

{analysis_context}

Instructions:
- Recommend 3-5 specific {category} products within the ${budget} budget
- Include real product names and estimated prices
- Consider the user's skin type, conditions, and goals
- Avoid ingredients they're allergic to
- Output as a JSON array with objects containing "name" and "price" fields
- Prices should be strings like "$25.99"
- No markdown or explanations, just return the JSON array

Example format:
[
  {{"name": "Product Name", "price": "$25.99"}},
  {{"name": "Another Product", "price": "$15.00"}}
]
"""

        try:
            response = self.model.generate_content(prompt)
            raw = getattr(response, 'text', '').strip()

            print(f"🧪 Raw {category} Response:\n", raw)

      
            if raw.startswith("```"):
                lines = raw.split('\n')  
                json_start = 1 if lines[0].startswith("```") else 0
                json_end = len(lines)
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].strip() == "```":
                        json_end = i
                        break
                raw = '\n'.join(lines[json_start:json_end]).strip()

            raw = raw.replace("```json", "").replace("```", "").strip()

            if not (raw.startswith('[') and raw.endswith(']')):
                import re
                json_match = re.search(r'\[.*?\]', raw, re.DOTALL)
                if json_match:
                    raw = json_match.group()

            parsed = json.loads(raw)
            print(f"💄 {category} products:", parsed)
            return parsed

        except Exception as e:
            print(f"❌ Failed to get {category} recommendations:", e)
            raise HTTPException(status_code=500, detail=f"Failed to get {category} recommendations")

    def get_future_recommendations(self, form_data: FormData, current_categories: List[str], skin_analysis=None) -> List[Dict[str, Any]]:
        """Get future recommendations - ORIGINAL LOGIC PRESERVED"""
        all_categories = [
            "facial_wash", "moisturizer", "sunscreen", "treatment", "toner",
            "serum", "eye_cream", "exfoliant", "mask", "essence", "ampoule"
        ]
        
        future_categories = [cat for cat in all_categories if cat not in current_categories]
        
        if not future_categories:
            return []

        analysis_context = ""
        if skin_analysis:
            analysis_context = f"""
Current Skin Analysis:
- Redness/Irritation: {getattr(skin_analysis, 'redness_irritation', 'N/A')}
- Acne Breakouts: {getattr(skin_analysis, 'acne_breakouts', 'N/A')}
- Oiliness/Shine: {getattr(skin_analysis, 'oiliness_shine', 'N/A')}
"""

        prompt = f"""
Based on the user's skincare profile, recommend future product categories they should consider adding to their routine.

User Profile:
- Skin Type: {', '.join(form_data.skin_type)}
- Goals: {', '.join(form_data.goals + ([form_data.custom_goal] if form_data.custom_goal else []))}
- Current Categories: {', '.join(current_categories)}
- Available Future Categories: {', '.join(future_categories)}

{analysis_context}

Instructions:
- Recommend 2-3 future product categories from the available list
- For each category, suggest 2-3 specific products
- Output as JSON array with objects containing "category" and "products" fields
- Products should have "name" and "price" fields
- No markdown or explanations, just return the JSON array

Format:
[
  {{
    "category": "serum",
    "products": [
      {{"name": "Product Name", "price": "$30.00"}},
      {{"name": "Another Product", "price": "$25.00"}}
    ]
  }}
]
"""

        try:
            response = self.model.generate_content(prompt)
            raw = getattr(response, 'text', '').strip()

            print("🧪 Raw Future Recommendations:\n", raw)

            if raw.startswith("```"):
                lines = raw.split('\n')
                json_start = 1 if lines[0].startswith("```") else 0
                json_end = len(lines)
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].strip() == "```":
                        json_end = i
                        break
                raw = '\n'.join(lines[json_start:json_end]).strip()

            raw = raw.replace("```json", "").replace("```", "").strip()

            parsed = json.loads(raw)
            print("🔮 Future recommendations:", parsed)
            return parsed

        except Exception as e:
            print("❌ Failed to parse future recommendations:", e)
            raise HTTPException(status_code=500, detail="Failed to generate future recommendations")
    
    async def enrich_products_with_details(self, products: Dict[str, List[Dict[str, Any]]], session_id: str, context: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for detailed product information and store in database.
        
        This method:
        1. Takes AI-recommended product names
        2. Searches for each product in the database cache
        3. If not found, fetches from SerpAPI and stores in cache
        4. Stores user's recommended products linked to session_id
        """
        enriched_products = {}
        
        try:
            for category, product_list in products.items():
                enriched_category = []
                
                for product in product_list:
                    product_name = product.get("name", "")
                    recommended_price = product.get("price", "$0.00")
                    
                    if not product_name:
                        continue
                    
                    print(f"🔍 Searching for product details: {product_name}")
                    
                    # Create recommendation context for this product
                    recommendation_context = {
                        "category": category,
                        "recommended_price": recommended_price,
                        "user_context": context,
                        "ai_recommended": True
                    }
                    
                    # Search for product details (cache first, then SerpAPI)
                    product_details = await product_search_service.get_or_fetch_product(
                        query=product_name,
                        session_id=session_id,
                        recommendation_context=recommendation_context
                    )
                    
                    if product_details:
                        # Combine AI recommendation with detailed product data
                        enriched_product = {
                            "ai_recommendation": product,  # Original AI recommendation
                            "product_details": product_details,  # Detailed product info from SerpAPI
                            "category": category,
                            "enriched_at": product_details.get("fetched_at"),
                            "search_successful": True
                        }
                        print(f"✅ Successfully enriched: {product_name}")
                    else:
                        # Keep original recommendation if search fails
                        enriched_product = {
                            "ai_recommendation": product,
                            "product_details": None,
                            "category": category,
                            "search_successful": False,
                            "error": "Product details not found"
                        }
                        print(f"⚠️  Could not find details for: {product_name}")
                    
                    enriched_category.append(enriched_product)
                
                enriched_products[category] = enriched_category
            
            return enriched_products
            
        except Exception as e:
            print(f"❌ Error enriching products: {e}")
            # Return original products if enrichment fails
            return {category: [{"ai_recommendation": p, "product_details": None, "search_successful": False} for p in products] for category, products in products.items()}
    
    async def enrich_future_recommendations(self, future_recommendations: List[Dict[str, Any]], session_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enrich future recommendations with product details"""
        enriched_future = []
        
        try:
            for recommendation in future_recommendations:
                category = recommendation.get("category", "")
                products = recommendation.get("products", [])
                
                enriched_products = []
                for product in products:
                    product_name = product.get("name", "")
                    
                    if product_name:
                        recommendation_context = {
                            "category": category,
                            "recommended_price": product.get("price", "$0.00"),
                            "user_context": context,
                            "ai_recommended": True,
                            "future_recommendation": True
                        }
                        
                        product_details = await product_search_service.get_or_fetch_product(
                            query=product_name,
                            session_id=session_id,
                            recommendation_context=recommendation_context
                        )
                        
                        enriched_product = {
                            "ai_recommendation": product,
                            "product_details": product_details,
                            "search_successful": product_details is not None
                        }
                        enriched_products.append(enriched_product)
                
                enriched_future.append({
                    "category": category,
                    "products": enriched_products
                })
            
            return enriched_future
            
        except Exception as e:
            print(f"❌ Error enriching future recommendations: {e}")
            return future_recommendations

    async def budget_distribution(self, data: dict, session_id: str) -> Dict[str, Any]:
        """
        Main budget distribution function with product search integration.
        
        ENHANCED WORKFLOW:
        1. Generate AI recommendations (original logic preserved)
        2. Search for each recommended product in database/SerpAPI
        3. Store detailed product information linked to session
        4. Return enriched recommendations with full product details
        """
        try:
            form_data = FormData(**data.get("form_data"))
            skin_analysis_data = data.get("skin_analysis")
            skin_analysis = None
            if skin_analysis_data:
                class SkinAnalysis:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                skin_analysis = SkinAnalysis(skin_analysis_data)

            # Step 1: Budget allocation (original logic preserved)
            allocation = self.get_budget_allocation(form_data)

            # Step 2: Convert total budget
            total_budget = float(form_data.budget.replace("$", "").strip())

            # Step 3: Generate AI product recommendations (original logic preserved)
            product_results = {}
            product_categories = list(allocation.keys())

            for category, percent in allocation.items():
                category_budget = round((percent / 100) * total_budget, 2)
                print(f"🧮 Budget for {category}: ${category_budget}")
                products = self.get_product_recommendations(category, category_budget, form_data, skin_analysis)
                product_results[category] = products

            # Step 4: Generate future recommendations (original logic preserved)
            future = self.get_future_recommendations(
                form_data,
                current_categories=product_categories,
                skin_analysis=skin_analysis
            )

            # Step 5: NEW - Enrich products with detailed information from database/SerpAPI
            print("🔍 Enriching products with detailed information...")
            user_context = {
                "skin_type": form_data.skin_type,
                "skin_conditions": form_data.skin_conditions,
                "budget": form_data.budget,
                "goals": form_data.goals
            }
            
            enriched_products = await self.enrich_products_with_details(
                products=product_results,
                session_id=session_id,
                context=user_context
            )
            
            enriched_future = await self.enrich_future_recommendations(
                future_recommendations=future,
                session_id=session_id,
                context=user_context
            )

            print("categories:", product_categories)
            print("✅ Product enrichment completed")

            # Step 6: Prepare response in original format for API compatibility
            # Store enriched data separately for database
            enriched_response = {
                "allocation": allocation,
                "products": enriched_products,  # Enriched version
                "total_budget": f"${total_budget}",
                "future_recommendations": enriched_future,
                "enrichment_summary": {
                    "total_products_searched": sum(len(products) for products in product_results.values()),
                    "session_id": session_id,
                    "search_completed": True
                }
            }
            
            # Return original format for API response (Pydantic validation)
            api_response = {
                "allocation": allocation,
                "products": product_results,  # Original format
                "total_budget": f"${total_budget}",
                "future_recommendations": future  # Original format
            }

            return {
                "api_response": api_response,  # For API response
                "enriched_data": enriched_response  # For database storage
            }

        except Exception as e:
            print("❌ Error in budget distribution:", str(e))
            raise HTTPException(status_code=500, detail="Failed to complete budget distribution phase")


# Global instance
phase3_service = Phase3Service()
