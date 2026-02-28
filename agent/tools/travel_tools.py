"""
Travel Utility Tools - Weather, Currency, etc.
"""

import requests
from typing import Dict, Optional
from google.adk.tools import AgentTool


@AgentTool
def get_weather(
    tool_context: ToolContext,
    location: str,
    date: Optional[str] = None
) -> Dict:
    """
    Get weather information for a location.

    Args:
        location: City or location name
        date: Optional date (YYYY-MM-DD format)

    Returns:
        Weather information including temperature, conditions, forecast
    """
    # Using Open-Meteo API (free, no API key needed)
    try:
        # First geocode the location
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        geo_response = requests.get(geocode_url, timeout=5).json()

        if not geo_response.get("results"):
            return {"error": f"Location '{location}' not found", "location": location}

        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["latitude"]
        name = geo_response["results"][0]["name"]

        # Get weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto"
        weather_response = requests.get(weather_url, timeout=5).json()

        current = weather_response.get("current", {})
        daily = weather_response.get("daily", {})

        # Weather code mapping
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle",
            53: "Moderate drizzle", 55: "Dense drizzle", 61: "Slight rain",
            63: "Moderate rain", 65: "Heavy rain", 80: "Slight rain showers",
            81: "Moderate rain showers", 82: "Violent rain showers", 95: "Thunderstorm"
        }

        current_condition = weather_codes.get(current.get("weather_code", 0), "Unknown")

        return {
            "location": name,
            "current": {
                "temperature": current.get("temperature_2m"),
                "condition": current_condition,
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m")
            },
            "forecast": [
                {
                    "date": daily.get("time", [])[i] if daily.get("time") else None,
                    "high": daily.get("temperature_2m_max", [])[i] if daily.get("temperature_2m_max") else None,
                    "low": daily.get("temperature_2m_min", [])[i] if daily.get("temperature_2m_min") else None,
                    "condition": weather_codes.get(daily.get("weather_code", [])[i], "Unknown") if daily.get("weather_code") else "Unknown"
                }
                for i in range(min(3, len(daily.get("time", []))))
            ]
        }
    except Exception as e:
        return {"error": str(e), "location": location}


@AgentTool
def convert_currency(
    tool_context: ToolContext,
    amount: float,
    from_currency: str = "USD",
    to_currency: str = "TND"
) -> Dict:
    """
    Convert currency amounts (approximate rates).

    Args:
        amount: Amount to convert
        from_currency: Source currency code (USD, EUR, TND, etc.)
        to_currency: Target currency code

    Returns:
        Conversion result with rate information
    """
    # Approximate exchange rates (in production, use an API)
    rates = {
        "USD": 1.0,
        "EUR": 0.92,
        "TND": 3.15,
        "GBP": 0.79,
        "CAD": 1.36,
        "CHF": 0.88,
        "MAD": 10.1,
        "DZD": 134.5,
        "EUR": 0.92
    }

    from_rate = rates.get(from_currency.upper(), 1.0)
    to_rate = rates.get(to_currency.upper(), 1.0)

    converted = (amount / from_rate) * to_rate
    rate = to_rate / from_rate

    return {
        "amount": amount,
        "from": from_currency.upper(),
        "to": to_currency.upper(),
        "result": round(converted, 2),
        "rate": round(rate, 4)
    }


@AgentTool
def create_itinerary(
    tool_context: ToolContext,
    destination: str,
    days: int,
    interests: Optional[str] = None,
    budget: Optional[str] = "medium"
) -> Dict:
    """
    Create a day-by-day travel itinerary.

    Args:
        destination: Destination name
        days: Number of days
        interests: Travel interests (culture, adventure, food, etc.)
        budget: Budget level (low/medium/high)

    Returns:
        Structured itinerary with daily plans
    """
    from database import QdrantManager

    qdrant = QdrantManager()

    # Get attractions for the destination
    query_text = f"attractions in {destination}"
    if interests:
        query_text += f" for {interests}"

    results = qdrant.search(
        collection_name="attractions",
        query_text=query_text,
        limit=days * 3
    )

    attractions = [r.payload for r in results]

    # Build itinerary
    itinerary = {"destination": destination, "days": days, "daily_plan": []}

    activities_per_day = max(1, len(attractions) // days)

    for day in range(days):
        day_attractions = attractions[day * activities_per_day:(day + 1) * activities_per_day]

        daily_plan = {
            "day": day + 1,
            "activities": [
                {
                    "time": "09:00",
                    "activity": a.get("name", "Explore"),
                    "description": a.get("description", ""),
                    "type": a.get("type", "sightseeing")
                }
                for a in day_attractions[:2]
            ],
            "lunch": "Local restaurant recommendation",
            "evening": "Free time to explore"
        }

        itinerary["daily_plan"].append(daily_plan)

    return itinerary
