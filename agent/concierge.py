"""
Tourism Concierge AI Agent using LangGraph with OpenAI
"""

from typing import TypedDict, Annotated, Sequence, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import tool
import operator

from utils.config import Config
from database import QdrantManager


# Agent State
class AgentState(TypedDict):
    """State for the tourism concierge agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_preferences: Dict[str, Any]
    search_results: Dict[str, Any]


class TourismConciergeAgent:
    """AI Tourism Concierge Agent using LangGraph"""

    # System prompt
    SYSTEM_PROMPT = """You are a friendly and knowledgeable AI Tourism Concierge for Tunisia and North Africa.

Your goal is to help tourists plan their perfect trip by providing:
- Destination recommendations based on interests, budget, and travel style
- Attraction information (historical sites, museums, natural wonders, beaches)
- Restaurant recommendations with local cuisine specialties
- Hotel and accommodation suggestions
- Weather information
- Currency conversion
- Custom itinerary creation

You have access to tools that can search our database of destinations, attractions, restaurants, and hotels.

Guidelines:
- Be enthusiastic and warm - tourists are planning their dream vacation!
- Provide specific, practical details (hours, prices, best times to visit)
- Suggest hidden gems and local experiences, not just tourist traps
- Consider budget constraints when making recommendations
- Ask follow-up questions if you need more information to give better recommendations

When a user asks for recommendations, think about:
- Their interests (culture, adventure, relaxation, food, etc.)
- Their budget level
- Their travel companions (solo, couple, family)
- The season they're traveling

Tunisia highlights to mention:
- Sidi Bou Said: Blue & white village with sea views
- Carthage: Ancient Roman ruins
- Sahara Desert: Camel treks and Star Wars locations
- Djerba: Island paradise with beautiful beaches
- El Jem: Massive Roman colosseum
- Kairouan: Holy city with Great Mosque

Always be helpful and aim to create memorable travel experiences!"""

    def __init__(self):
        """Initialize the agent"""
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=Config.CHAT_MODEL,
            api_key=Config.OPENAI_API_KEY,
            temperature=0.7
        )

        # Initialize database
        self.db = QdrantManager()

        # Create tools
        self.tools = self._create_tools()

        # Build the graph
        self.graph = self._build_graph()

    def _create_tools(self) -> List:
        """Create agent tools"""

        @tool
        def search_destinations_tool(query: str, region: str = "Tunisia", budget_level: str = "medium") -> str:
            """Search for destinations matching the query.
            Args:
                query: Search query (e.g., "beach destinations", "historical sites")
                region: Geographic region (default: Tunisia)
                budget_level: Budget preference - low/medium/high"""
            results = self.db.search(
                collection_name="destinations",
                query_text=f"{query} in {region}",
                limit=5
            )

            if not results:
                return f"No destinations found matching '{query}' in {region}."

            output = f"Found {len(results)} destinations:\n\n"
            for r in results:
                dest = r.payload
                output += f"**{dest.get('name', 'Unknown')}** (similarity: {r.score:.2f})\n"
                output += f"{dest.get('description', 'No description')}\n"
                output += f"Best season: {dest.get('best_season', 'N/A')}\n"
                output += f"Activities: {', '.join(dest.get('activities', []))}\n\n"

            return output

        @tool
        def get_attractions_tool(destination: str, attraction_type: str = "") -> str:
            """Get attractions for a destination.
            Args:
                destination: Name of the destination
                attraction_type: Optional filter by type (museum, beach, historical, nature)"""
            query = f"attractions in {destination}"
            if attraction_type:
                query += f" {attraction_type}"

            results = self.db.search(
                collection_name="attractions",
                query_text=query,
                limit=8
            )

            if not results:
                return f"No attractions found in {destination}."

            output = f"Top attractions in {destination}:\n\n"
            for r in results:
                attr = r.payload
                output += f"**{attr.get('name', 'Unknown')}** ({attr.get('type', 'attraction')})\n"
                output += f"{attr.get('description', 'No description')}\n"
                output += f"Rating: {attr.get('rating', 'N/A')}/5 | Hours: {attr.get('opening_hours', 'N/A')}\n"
                output += f"Entry fee: {attr.get('entry_fee', 'N/A')}\n\n"

            return output

        @tool
        def get_weather_tool(location: str) -> str:
            """Get current weather and forecast for a location.
            Args:
                location: City or location name"""
            import requests

            try:
                # Geocode
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
                geo_response = requests.get(geo_url, timeout=5).json()

                if not geo_response.get("results"):
                    return f"Location '{location}' not found."

                name = geo_response["results"][0]["name"]
                lat = geo_response["results"][0]["latitude"]
                lon = geo_response["results"][0]["longitude"]

                # Weather
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto"
                weather_response = requests.get(weather_url, timeout=5).json()

                current = weather_response.get("current", {})
                daily = weather_response.get("daily", {})

                weather_codes = {
                    0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                    45: "Foggy", 51: "Light drizzle", 61: "Rain", 80: "Rain showers",
                    95: "Thunderstorm", 71: "Snow", 77: "Snow grains"
                }

                condition = weather_codes.get(current.get("weather_code", 0), "Unknown")

                output = f"Weather in {name}:\n\n"
                output += f"Currently: {current.get('temperature_2m', 'N/A')}°C, {condition}\n"
                output += f"Humidity: {current.get('relative_humidity_2m', 'N/A')}% | "
                output += f"Wind: {current.get('wind_speed_10m', 'N/A')} km/h\n\n"
                output += "Forecast:\n"

                for i in range(min(3, len(daily.get("time", [])))):
                    date = daily.get("time", [])[i]
                    high = daily.get("temperature_2m_max", [])[i]
                    low = daily.get("temperature_2m_min", [])[i]
                    cond = weather_codes.get(daily.get("weather_code", [])[i], "Unknown")
                    output += f"  {date}: {cond}, {high}°C/{low}°C\n"

                return output

            except Exception as e:
                return f"Error getting weather: {str(e)}"

        @tool
        def convert_currency_tool(amount: float, from_currency: str = "USD", to_currency: str = "TND") -> str:
            """Convert currency amounts (approximate rates).
            Args:
                amount: Amount to convert
                from_currency: Source currency (USD, EUR, TND, etc.)
                to_currency: Target currency"""
            rates = {
                "USD": 1.0, "EUR": 0.92, "TND": 3.15, "GBP": 0.79,
                "CAD": 1.36, "CHF": 0.88, "MAD": 10.1, "DZD": 134.5
            }

            from_rate = rates.get(from_currency.upper(), 1.0)
            to_rate = rates.get(to_currency.upper(), 1.0)
            converted = (amount / from_rate) * to_rate

            return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()} (Rate: 1 {from_currency.upper()} = {to_rate/from_rate:.4f} {to_currency.upper()})"

        @tool
        def recommend_restaurants_tool(location: str, cuisine_type: str = "", price_range: str = "medium") -> str:
            """Recommend restaurants at a location.
            Args:
                location: City or area name
                cuisine_type: Type of cuisine (optional)
                price_range: budget/medium/high-end"""
            query = f"restaurants in {location}"
            if cuisine_type:
                query += f" {cuisine_type} cuisine"
            if price_range:
                query += f" {price_range} price"

            results = self.db.search(
                collection_name="restaurants",
                query_text=query,
                limit=5
            )

            if not results:
                return f"No restaurants found in {location}."

            output = f"Restaurant recommendations in {location}:\n\n"
            for r in results:
                rest = r.payload
                output += f"**{rest.get('name', 'Unknown')}** ({rest.get('cuisine', 'various')})\n"
                output += f"{rest.get('description', 'No description')}\n"
                output += f"Price: {rest.get('price_range', 'N/A')} | Rating: {rest.get('rating', 'N/A')}/5\n"
                output += f"Specialties: {', '.join(rest.get('specialties', []))}\n\n"

            return output

        @tool
        def recommend_hotels_tool(location: str, budget_level: str = "medium", accommodation_type: str = "") -> str:
            """Recommend hotels/accommodations at a location.
            Args:
                location: City or area name
                budget_level: budget/medium/luxury
                accommodation_type: hotel/riad/resort (optional)"""
            query = f"hotels in {location}"
            if accommodation_type:
                query += f" {accommodation_type}"
            if budget_level:
                query += f" {budget_level}"

            results = self.db.search(
                collection_name="hotels",
                query_text=query,
                limit=5
            )

            if not results:
                return f"No hotels found in {location}."

            output = f"Hotel recommendations in {location}:\n\n"
            for r in results:
                hotel = r.payload
                output += f"**{hotel.get('name', 'Unknown')}** ({hotel.get('type', 'hotel')})\n"
                output += f"{hotel.get('description', 'No description')}\n"
                output += f"Price: {hotel.get('price_range', 'N/A')} | Rating: {hotel.get('rating', 'N/A')}/5\n"
                output += f"Amenities: {', '.join(hotel.get('amenities', []))}\n\n"

            return output

        @tool
        def create_itinerary_tool(destination: str, days: int, interests: str = "general") -> str:
            """Create a day-by-day travel itinerary.
            Args:
                destination: Destination name
                days: Number of days
                interests: Travel interests (culture, adventure, food, beach, etc.)"""
            # Get attractions
            query = f"attractions in {destination} for {interests} travel"
            results = self.db.search(
                collection_name="attractions",
                query_text=query,
                limit=days * 3
            )

            attractions = [r.payload for r in results]

            output = f"**{days}-Day Itinerary for {destination}**\n\n"

            activities_per_day = max(1, len(attractions) // days)

            for day in range(days):
                day_attractions = attractions[day * activities_per_day:(day + 1) * activities_per_day]

                output += f"### Day {day + 1}\n"

                if day_attractions:
                    morning = day_attractions[0] if len(day_attractions) > 0 else None
                    afternoon = day_attractions[1] if len(day_attractions) > 1 else None

                    if morning:
                        output += f"- **Morning**: Visit {morning.get('name', 'local attraction')} - {morning.get('description', '')[:100]}...\n"
                    if afternoon:
                        output += f"- **Afternoon**: Explore {afternoon.get('name', 'local attraction')} - {afternoon.get('description', '')[:100]}...\n"

                output += f"- **Lunch**: Try a local restaurant\n"
                output += f"- **Evening**: Free time to explore, enjoy local cuisine, or relax\n\n"

            if not attractions:
                output += f"Note: Limited attraction data for {destination}. The agent can help you find more specific activities!\n"

            return output

        return [
            search_destinations_tool,
            get_attractions_tool,
            get_weather_tool,
            convert_currency_tool,
            recommend_restaurants_tool,
            recommend_hotels_tool,
            create_itinerary_tool
        ]

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph agent graph"""

        def call_model(state: AgentState) -> AgentState:
            """Call the LLM with tools"""
            messages = state["messages"]
            response = self.llm.invoke(messages)
            return {"messages": [response]}

        def should_continue(state: AgentState) -> str:
            """Determine if we should continue calling tools"""
            messages = state["messages"]
            last_message = messages[-1]

            if last_message.tool_calls:
                return "tools"
            return END

        # Build graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        # Set entry point
        workflow.set_entry_point("agent")

        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )

        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def chat(self, message: str, history: List[Dict[str, str]] = None) -> str:
        """Chat with the agent

        Args:
            message: User message
            history: Optional chat history as list of {"role": "user|assistant", "content": "..."}

        Returns:
            Agent response
        """
        # Build messages
        messages = [SystemMessage(content=self.SYSTEM_PROMPT)]

        # Add history
        if history:
            for item in history[-5:]:  # Keep last 5 messages
                if item["role"] == "user":
                    messages.append(HumanMessage(content=item["content"]))
                elif item["role"] == "assistant":
                    messages.append(AIMessage(content=item["content"]))

        # Add current message
        messages.append(HumanMessage(content=message))

        # Invoke graph
        result = self.graph.invoke({"messages": messages})

        # Get last AI message
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        if ai_messages:
            return ai_messages[-1].content

        return "I apologize, but I couldn't process your request. Please try again."

    def chat_stream(self, message: str, history: List[Dict[str, str]] = None):
        """Stream chat responses for real-time UI updates

        Args:
            message: User message
            history: Optional chat history

        Yields:
            Response chunks
        """
        # Build messages
        messages = [SystemMessage(content=self.SYSTEM_PROMPT)]

        if history:
            for item in history[-5:]:
                if item["role"] == "user":
                    messages.append(HumanMessage(content=item["content"]))
                elif item["role"] == "assistant":
                    messages.append(AIMessage(content=item["content"]))

        messages.append(HumanMessage(content=message))

        # Stream from graph
        for event in self.graph.stream({"messages": messages}):
            for node_name, node_output in event.items():
                if node_name == "agent":
                    for msg in node_output.get("messages", []):
                        if isinstance(msg, AIMessage) and msg.content:
                            yield msg.content


def create_agent() -> TourismConciergeAgent:
    """Factory function to create the agent"""
    return TourismConciergeAgent()
