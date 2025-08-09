"""
Skincare Router

Professional router for AI-powered skincare analysis pipeline.
4-phase system: Form Input → Image Analysis → Product Recommendations → Routine Creation
Each phase stores results in JSON for the next phase.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from typing import Dict, Any, Optional
from datetime import datetime
import json

from ..models.skincare.form_schemas import FormData
from ..models.skincare.analysis_schemas import FaceAnalysisResponse, SkincareRoutineResponse
from ..models.skincare.recommendation_schemas import ProductRecommendationResponse
from ..services.form_processing_service import phase1_service
from ..services.image_analysis_service import phase2_service
from ..services.product_recommendation_service import phase3_service
from ..services.routine_creation_service import phase4_service
from ..services.product_search_service import product_search_service
from ..core.database import Database
from ..connection_logic import data_store

router = APIRouter(prefix="/skincare", tags=["Skincare AI Pipeline"])


# ===== INPUT ENDPOINTS =====

@router.post("/phase1/form-analysis", 
             status_code=status.HTTP_201_CREATED,
             summary="Phase 1: Submit Skincare Form",
             description="Submit user skincare form data. Creates a session and stores form data for subsequent phases.")
async def phase1_form_analysis(form_data: FormData) -> Dict[str, Any]:
    """
    **Phase 1: Form Data Collection**
    
    Input endpoint that processes user form data including:
    - Skin type and conditions
    - Budget and goals
    - Product experiences and allergies
    
    Creates a session ID and stores the form data as JSON for Phase 2 & 3.
    """
    try:
        # Use original phase1 logic (preserved)
        result = phase1_service.submit_form(form_data)
        
        # Create session and save data for pipeline
        session_id = data_store.create_session()
        form_dict = result["stored_data"].dict() if hasattr(result["stored_data"], 'dict') else result["stored_data"]
        
        success = await data_store.save_phase_data(session_id, "phase1", form_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save form data"
            )
        
        return {
            "session_id": session_id,
            "status": "success",
            "message": "Form data processed and saved successfully",
            "next_phase": "Phase 2: Upload facial image for analysis",
            "form_index": result["form_index"],
            "data": form_dict
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Phase 1 failed: {str(e)}"
        )


@router.post("/phase2/image-analysis",
             status_code=status.HTTP_200_OK,
             summary="Phase 2: Facial Image Analysis", 
             description="Analyze uploaded facial image for skin assessment. Requires session from Phase 1.")
async def phase2_image_analysis(session_id: str, file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    **Phase 2: AI Image Analysis**
    
    Input endpoint that analyzes facial images using AI to detect:
    - Skin conditions (acne, dryness, oiliness)
    - Skin tone and texture
    - Problem areas and concerns
    
    Stores analysis results as JSON for Phase 3.
    """
    try:

        if not await data_store.session_exists(session_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found. Complete Phase 1 first."
            )
        
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read and analyze image using original phase2 logic (preserved)
        image_data = await file.read()
        analysis_result = await phase2_service.analyze_face(image_data)
        
        # Extract analysis data from response
        if hasattr(analysis_result, 'body'):
            analysis_json = json.loads(analysis_result.body.decode())
        else:
            analysis_json = analysis_result
        
        # Save analysis for Phase 3
        success = await data_store.save_phase_data(session_id, "phase2", analysis_json)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save analysis data"
            )
        
        return {
            "session_id": session_id,
            "status": "success",
            "message": "Image analysis completed and saved successfully",
            "next_phase": "Phase 3: Generate product recommendations",
            "analysis": analysis_json
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Phase 2 failed: {str(e)}"
        )


# ===== OUTPUT ENDPOINTS =====

@router.post("/phase3/product-recommendations",
             status_code=status.HTTP_200_OK,
             response_model=ProductRecommendationResponse,
             summary="Phase 3: Generate Product Recommendations",
             description="Generate personalized product recommendations based on form data and image analysis.")
async def phase3_product_recommendations(session_id: str) -> ProductRecommendationResponse:
    """
    **Phase 3: Product Recommendation Engine**
    
    Output endpoint that generates personalized product recommendations by:
    - Combining form data (Phase 1) and image analysis (Phase 2)
    - Allocating budget across product categories
    - Finding specific products within budget
    - Providing future recommendations
    
    Stores recommendations as JSON for Phase 4.
    """
    try:
        # Get data from previous phases
        form_data = await data_store.load_phase_data(session_id, "phase1")
        analysis_data = await data_store.load_phase_data(session_id, "phase2")
        
        if not form_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing form data. Complete Phase 1 first."
            )
        
        if not analysis_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing image analysis. Complete Phase 2 first."
            )
        
        # Prepare data for phase3 service (original format preserved)
        phase3_input = {
            "form_data": form_data,
            "skin_analysis": analysis_data.get("ai_output", analysis_data)
        }
        
        # Use enhanced phase3 logic with product search integration
        phase3_result = await phase3_service.budget_distribution(phase3_input, session_id)
        
        # Extract the API response and enriched data
        api_response = phase3_result["api_response"]
        enriched_data = phase3_result["enriched_data"]
        
        # Save enriched data to database (includes detailed product info)
        success = await data_store.save_phase_data(session_id, "phase3", enriched_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save recommendations"
            )
        
        # Return structured response (original format for Pydantic validation)
        return ProductRecommendationResponse(**api_response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Phase 3 failed: {str(e)}"
        )


@router.post("/phase4/routine-creation",
             status_code=status.HTTP_200_OK,
             response_model=SkincareRoutineResponse,
             summary="Phase 4: Create Skincare Routine",
             description="Create personalized skincare routine based on recommended products.")
async def phase4_routine_creation(session_id: str) -> SkincareRoutineResponse:
    """
    **Phase 4: Routine Creation Engine**
    
    Output endpoint that creates a personalized skincare routine by:
    - Using form preferences (Phase 1) and product recommendations (Phase 3)
    - Creating morning and evening routines
    - Providing step-by-step instructions
    - Including timing and frequency guidance
    
    Stores final routine as JSON.
    """
    try:
        # Get data from previous phases
        form_data = await data_store.load_phase_data(session_id, "phase1")
        recommendations = await data_store.load_phase_data(session_id, "phase3")
        
        if not form_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing form data. Complete Phase 1 first."
            )
        
        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing product recommendations. Complete Phase 3 first."
            )
        
        # Prepare data for phase4 service (original format preserved)
        phase4_input = {
            "form_data": form_data,
            "product_recommendations": recommendations.get("products", {})
        }
        
        # Use original phase4 logic (preserved)
        routine_result = phase4_service.create_routine(phase4_input)
        
        # Save final routine
        success = await data_store.save_phase_data(session_id, "phase4", routine_result)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save routine"
            )
        
        # Return structured response
        return SkincareRoutineResponse(**routine_result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Phase 4 failed: {str(e)}"
        )


# ===== UTILITY ENDPOINTS =====

@router.get("/session/{session_id}/status",
            status_code=status.HTTP_200_OK,
            summary="Check Session Status",
            description="Get the current status and progress of a skincare analysis session.")
async def get_session_status(session_id: str) -> Dict[str, Any]:
    """
    **Session Status Checker**
    
    Utility endpoint that shows:
    - Which phases have been completed
    - Available data for each phase
    - Next recommended phase
    """
    try:
        if not await data_store.session_exists(session_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        phase_status_result = await data_store.get_session_status(session_id)
        phase_status = phase_status_result.get("phases", {})
        completed_phases = [phase for phase, completed in phase_status.items() if completed]
        
        # Determine next phase
        next_phase = None
        if not phase_status.get("phase1", False):
            next_phase = "Phase 1: Submit form data"
        elif not phase_status.get("phase2", False):
            next_phase = "Phase 2: Upload facial image"
        elif not phase_status.get("phase3", False):
            next_phase = "Phase 3: Generate product recommendations"
        elif not phase_status.get("phase4", False):
            next_phase = "Phase 4: Create skincare routine"
        else:
            next_phase = "Pipeline complete!"
        
        return {
            "session_id": session_id,
            "completed_phases": completed_phases,
            "total_phases": 4,
            "progress_percentage": phase_status_result.get("progress_percentage", 0),
            "next_phase": next_phase,
            "phase_details": phase_status,
            "pipeline_complete": len(completed_phases) == 4
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )


@router.get("/forms",
            status_code=status.HTTP_200_OK,
            summary="List All Forms (Debug)",
            description="Debug endpoint to list all submitted forms.")
async def list_forms() -> Dict[str, Any]:
    """Debug endpoint to list all submitted forms"""
    try:
        forms = phase1_service.list_forms()
        return {
            "total_forms": len(forms),
            "forms": forms
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list forms: {str(e)}"
        )


# ===== PRODUCT MANAGEMENT ENDPOINTS =====

@router.get("/sessions/{session_id}/recommended-products",
            status_code=status.HTTP_200_OK,
            summary="Get User's Recommended Products",
            description="Retrieve all products recommended for a specific session with detailed information.")
async def get_user_recommended_products(session_id: str) -> Dict[str, Any]:
    """
    **Product Management: Get Session's Recommended Products**
    
    Returns all products that were recommended and searched for this session:
    - AI recommended products with detailed SerpAPI data
    - Product categories and prices
    - Recommendation context and timestamps
    """
    try:
        if not await data_store.session_exists(session_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get user's recommended products from database
        recommended_products = await product_search_service.get_user_recommended_products(session_id)
        
        # Get session status for context
        session_status = await data_store.get_session_status(session_id)
        
        return {
            "session_id": session_id,
            "total_recommended_products": len(recommended_products),
            "session_progress": session_status.get("progress_percentage", 0),
            "recommended_products": recommended_products,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recommended products: {str(e)}"
        )


@router.get("/products/cache-stats",
            status_code=status.HTTP_200_OK,
            summary="Product Cache Statistics",
            description="Get statistics about the products cache and user recommendations.")
async def get_product_cache_stats() -> Dict[str, Any]:
    """
    **Product Management: Cache Statistics**
    
    Returns statistics about:
    - Total products in cache
    - Total user recommendations
    - Recent activity
    """
    try:
        db = Database.get_database()
        
        # Count products in cache
        products_cache = db["products_cache"]
        cache_count = await products_cache.count_documents({})
        
        # Count user recommendations
        user_products = db["user_recommended_products"]
        user_recommendations_count = await user_products.count_documents({})
        
        # Get recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_cache_additions = await products_cache.count_documents({
            "cached_at": {"$gte": week_ago}
        })
        
        recent_user_recommendations = await user_products.count_documents({
            "recommended_at": {"$gte": week_ago}
        })
        
        return {
            "products_cache": {
                "total_products": cache_count,
                "recent_additions": recent_cache_additions
            },
            "user_recommendations": {
                "total_recommendations": user_recommendations_count,
                "recent_recommendations": recent_user_recommendations
            },
            "stats_generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache statistics: {str(e)}"
        )


@router.get("/products/search",
            response_model=Dict[str, Any],
            status_code=status.HTTP_200_OK,
            summary="Search Product Details",
            description="Search for a specific product and get enriched details from cache or SerpAPI.")
async def search_product_details(
    query: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    **Product Management: Search Product Details**
    
    Search for a product by name/query and get enriched details including:
    - Title, price, rating, reviews
    - Product link and thumbnail
    - Full description and specifications
    - Store information and availability
    
    If session_id is provided, the search will be saved to user recommendations.
    """
    try:
        product_data = await product_search_service.get_or_fetch_product(
            query=query,
            session_id=session_id,
            recommendation_context={
                "search_type": "manual_search",
                "ai_recommended": False
            } if session_id else None
        )
        
        if not product_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{query}' not found"
            )
        
        return {
            "search_query": query,
            "product_found": True,
            "product_details": product_data,
            "searched_at": datetime.utcnow().isoformat(),
            "cached": product_data.get("source") != "shopping_results" or "cached_at" in product_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search product: {str(e)}"
        )
