"""
Destination and Attraction Tools for Tourism Agent
"""

from typing import List, Dict, Optional
from google.adk.tools import AgentTool
from ..callback_context import CallbackContext


@AgentTool
def search_destinations(
    tool_context: ToolContext,
    query: str,
    region: Optional[str] = None,
    budget_level: Optional[str] = None,
    travel_type: Optional[str] = None
) -> Dict:
    """
    Search for tourist destinations matching the query.

    Args:
        query: Search query (e.g., "beach destinations", "historical sites")
        region: Geographic region to focus on (e.g., "Tunisia", "North Africa")
        budget_level: Budget preference (low/medium/high)
        travel_type: Type of travel (adventure/relaxation/cultural/family)

    Returns:
        Dictionary with matching destinations and details
    """
    # Import QdrantManager here to avoid circular imports
    from database import QdrantManager

    qdrant = QdrantManager()

    # Build search query
    search_text = query
    if region:
        search_text += f" in {region}"
    if travel_type:
        search_text += f" for {travel_type} travel"

    # Search vector database
    results = qdrant.search(
        collection_name="destinations",
        query_text=search_text,
        limit=5,
        filter={
            "budget_level": budget_level
        } if budget_level else None
    )

    destinations = []
    for result in results:
        destinations.append({
            "name": result.payload.get("name"),
            "description": result.payload.get("description"),
            "region": result.payload.get("region"),
            "best_season": result.payload.get("best_season"),
            "budget_level": result.payload.get("budget_level"),
            "activities": result.payload.get("activities", []),
            "score": result.score
        })

    return {
        "query": query,
        "destinations": destinations,
        "count": len(destinations)
    }


@AgentTool
def get_attractions(
    tool_context: ToolContext,
    destination: str,
    attraction_type: Optional[str] = None
) -> Dict:
    """
    Get attractions for a specific destination.

    Args:
        destination: Name of the destination
        attraction_type: Type of attraction (museum/beach/historical/nature)

    Returns:
        Dictionary with attractions and details
    """
    from database import QdrantManager

    qdrant = QdrantManager()

    query_text = f"attractions in {destination}"
    if attraction_type:
        query_text += f" {attraction_type}"

    results = qdrant.search(
        collection_name="attractions",
        query_text=query_text,
        limit=8
    )

    attractions = []
    for result in results:
        attractions.append({
            "name": result.payload.get("name"),
            "type": result.payload.get("type"),
            "description": result.payload.get("description"),
            "rating": result.payload.get("rating"),
            "entry_fee": result.payload.get("entry_fee"),
            "opening_hours": result.payload.get("opening_hours"),
            "location": result.payload.get("location"),
            "score": result.score
        })

    return {
        "destination": destination,
        "attractions": attractions,
        "count": len(attractions)
    }
