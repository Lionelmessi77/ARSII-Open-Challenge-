"""
Recommendation Tools - Restaurants, Hotels, etc.
"""

from typing import List, Dict, Optional
from google.adk.tools import AgentTool


@AgentTool
def recommend_restaurants(
    tool_context: ToolContext,
    location: str,
    cuisine_type: Optional[str] = None,
    price_range: Optional[str] = "medium"
) -> Dict:
    """
    Recommend restaurants at a location.

    Args:
        location: City or area name
        cuisine_type: Type of cuisine (Tunisian, Italian, Seafood, etc.)
        price_range: Price range (budget/medium/high-end)

    Returns:
        List of restaurant recommendations
    """
    from database import QdrantManager

    qdrant = QdrantManager()

    query_text = f"restaurants in {location}"
    if cuisine_type:
        query_text += f" {cuisine_type} cuisine"
    if price_range:
        query_text += f" {price_range} price"

    results = qdrant.search(
        collection_name="restaurants",
        query_text=query_text,
        limit=5
    )

    restaurants = []
    for result in results:
        restaurants.append({
            "name": result.payload.get("name"),
            "cuisine": result.payload.get("cuisine"),
            "description": result.payload.get("description"),
            "price_range": result.payload.get("price_range"),
            "rating": result.payload.get("rating"),
            "location": result.payload.get("location"),
            "specialties": result.payload.get("specialties", []),
            "score": result.score
        })

    return {
        "location": location,
        "restaurants": restaurants,
        "count": len(restaurants)
    }


@AgentTool
def recommend_hotels(
    tool_context: ToolContext,
    location: str,
    budget_level: Optional[str] = "medium",
    accommodation_type: Optional[str] = None
) -> Dict:
    """
    Recommend hotels/accommodations at a location.

    Args:
        location: City or area name
        budget_level: Budget level (budget/medium/luxury)
        accommodation_type: Type (hotel/riad/resort/appartment)

    Returns:
        List of accommodation recommendations
    """
    from database import QdrantManager

    qdrant = QdrantManager()

    query_text = f"hotels in {location}"
    if accommodation_type:
        query_text += f" {accommodation_type}"
    if budget_level:
        query_text += f" {budget_level}"

    results = qdrant.search(
        collection_name="hotels",
        query_text=query_text,
        limit=5
    )

    hotels = []
    for result in results:
        hotels.append({
            "name": result.payload.get("name"),
            "type": result.payload.get("type"),
            "description": result.payload.get("description"),
            "price_range": result.payload.get("price_range"),
            "rating": result.payload.get("rating"),
            "amenities": result.payload.get("amenities", []),
            "location": result.payload.get("location"),
            "score": result.score
        })

    return {
        "location": location,
        "hotels": hotels,
        "count": len(hotels)
    }
