"""
AI Tourism Concierge - Streamlit Frontend
An all-in-one travel planning assistant for Tunisia
Now with 3D World Generation via World Labs!
"""

import streamlit as st
from typing import List, Dict
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from agent.concierge import create_agent
    from database import QdrantManager
    from world_labs import WorldLabsClient, TUNISIA_WORLD_PROMPTS
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please install dependencies: `uv pip install -r requirements.txt`")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI Tourism Concierge",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .world-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .asset-image {
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        width: 100%;
    }
    /* Fix feature cards text color */
    div[data-testid="stVerticalBlock"] > div:has(> div > h3) {
        color: #333 !important;
    }
    .feature-card h3 {
        color: #333 !important;
    }
    .feature-card p {
        color: #666 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        with st.spinner("Initializing AI Concierge..."):
            try:
                st.session_state.agent = create_agent()
            except Exception as e:
                st.session_state.agent = None
                st.error(f"Failed to initialize agent: {e}")
    if "preferences" not in st.session_state:
        st.session_state.preferences = {
            "destination": "",
            "budget": "medium",
            "interests": [],
            "days": 3
        }
    if "generated_worlds" not in st.session_state:
        st.session_state.generated_worlds = {}
    if "world_labs_client" not in st.session_state:
        try:
            st.session_state.world_labs_client = WorldLabsClient()
        except Exception as e:
            st.session_state.world_labs_client = None
            st.warning(f"World Labs not available: {e}")

init_session_state()


# Helper function to generate AI response
def generate_response(user_message: str) -> str:
    """Generate a response from the AI agent"""
    if st.session_state.agent is None:
        return "I apologize, but the AI agent is not available. Please check your configuration."

    try:
        return st.session_state.agent.chat(
            message=user_message,
            history=st.session_state.messages
        )
    except Exception as e:
        return f"I encountered an error: {str(e)}\n\nPlease try rephrasing your question."


# Header
def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🌍 AI Tourism Concierge</h1>
        <p>Your personal travel assistant for exploring Tunisia and North Africa</p>
        <p style="font-size: 0.9em; opacity: 0.9;">✨ Now with 3D World Generation!</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Destinations", "8+", "Beautiful locations")
    with col2:
        st.metric("Attractions", "50+", "Points of interest")
    with col3:
        st.metric("Restaurants", "20+", "Local cuisines")
    with col4:
        st.metric("Hotels", "15+", "Accommodations")
    with col5:
        st.metric("3D Worlds", "10", "Immersive experiences")

    st.markdown("---")


# 3D World Generator Page
def render_3d_worlds():
    """Render the 3D World Generator page"""
    st.markdown("## 🎬 3D World Generator")
    st.markdown("Generate immersive 3D experiences of Tunisian destinations using World Labs AI!")

    # Check if World Labs is available
    if st.session_state.world_labs_client is None:
        st.error("""
        World Labs API key not found. Please add WORLD_LABS to your .env file.

        You can get an API key from: https://platform.worldlabs.ai/api-keys
        """)
        return

    # Two columns: selector and viewer
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 📍 Select Destination")

        # Destination selector
        destination_names = {
            "sidi_bou_said": "🔵 Sidi Bou Said - Blue Village",
            "el_jem": "🏛️ El Jem - Roman Colosseum",
            "carthage": "🏺 Ancient Carthage Ruins",
            "sahara_douz": "🏜️ Sahara Desert - Douz",
            "djerba": "🏝️ Djerba Island Paradise",
            "kairouan": "🕌 Kairouan - Holy City",
            "medina_tunis": "🏪 Medina of Tunis",
            "hammamet": "🏖️ Hammamet Beach Resort",
            "matmata": "⛰️ Matmata - Underground Homes",
            "ichkeul": "🦩 Ichkeul National Park"
        }

        selected_dest = st.selectbox(
            "Choose a destination to generate in 3D:",
            options=list(destination_names.keys()),
            format_func=lambda x: destination_names[x]
        )

        # Show description
        dest_info = TUNISIA_WORLD_PROMPTS[selected_dest]
        st.markdown(f"**{dest_info['name']}**")
        st.markdown(f"<small>{dest_info['prompt'][:150]}...</small>", unsafe_allow_html=True)

        st.markdown("---")

        # Model selection
        model = st.radio(
            "Quality vs Speed",
            options=["Marble 0.1-mini", "Marble 0.1-plus"],
            index=0,
            help="mini = ~30-45 seconds, plus = ~5 minutes (higher quality)"
        )

        # Generate button
        if st.button("🎬 Generate 3D World", type="primary", use_container_width=True):
            with st.spinner(f"Generating 3D world for {dest_info['name']}... This may take a few minutes."):
                try:
                    # Start generation
                    operation = st.session_state.world_labs_client.generate_world(
                        display_name=dest_info["name"],
                        text_prompt=dest_info["prompt"],
                        model=model
                    )

                    operation_id = operation["operation_id"]
                    st.info(f"Generation started! Operation ID: {operation_id}")

                    # Create a placeholder for progress
                    progress_placeholder = st.empty()
                    progress_placeholder.info("⏳ Processing... (this takes 2-5 minutes)")

                    # Poll for completion
                    start_time = time.time()
                    timeout = 400 if "plus" in model else 120  # Longer timeout for plus model

                    while time.time() - start_time < timeout:
                        completed_op = st.session_state.world_labs_client.get_operation(operation_id)

                        if completed_op.get("done"):
                            if completed_op.get("error"):
                                st.error(f"Generation failed: {completed_op['error']}")
                                break

                            # Success! Get world_id from response or metadata
                            world_data = completed_op.get("response", {})

                            # World Labs API uses "world_id" not "id" in the response
                            world_id = (
                                world_data.get("world_id") or  # Correct key!
                                completed_op.get("metadata", {}).get("world_id") or
                                completed_op.get("world_id")
                            )

                            if not world_id:
                                st.error(f"Could not extract world_id from response")
                                st.json(completed_op)
                                break

                            # Use world_marble_url from response if available
                            viewer_url = world_data.get("world_marble_url") or st.session_state.world_labs_client.get_world_viewer_url(world_id)

                            # Fetch full world details to get all assets
                            try:
                                time.sleep(2)  # Wait a bit for assets to be ready
                                full_world = st.session_state.world_labs_client.get_world(world_id)
                                assets = full_world.get("assets", {})
                            except:
                                assets = world_data.get("assets", {})

                            # Store in session
                            st.session_state.generated_worlds[selected_dest] = {
                                "world_id": world_id,
                                "viewer_url": viewer_url,
                                "thumbnail": assets.get("thumbnail_url", ""),
                                "pano_url": assets.get("imagery", {}).get("pano_url", ""),
                                "caption": assets.get("caption", ""),
                                "created_at": completed_op.get("updated_at", ""),
                                "assets": assets,
                                "display_name": dest_info["name"]
                            }

                            progress_placeholder.success("✅ World generated successfully!")
                            st.rerun()
                            break

                        # Show progress
                        progress = completed_op.get("metadata", {}).get("progress", {})
                        status = progress.get("status", "IN_PROGRESS")
                        progress_placeholder.info(f"⏳ Status: {status}...")

                        time.sleep(10)  # Poll every 10 seconds
                    else:
                        progress_placeholder.error("⏱️ Generation timed out. Please try again.")

                except Exception as e:
                    st.error(f"Error generating world: {e}")
                    import traceback
                    st.text(traceback.format_exc())

        st.markdown("---")

        # Show generated worlds list
        if st.session_state.generated_worlds:
            st.markdown("### 📚 Your Generated Worlds")
            for dest_key, world_info in st.session_state.generated_worlds.items():
                with st.expander(destination_names.get(dest_key, dest_key)):
                    st.markdown(f"**World ID:** `{world_info.get('world_id', 'N/A')}`")
                    st.markdown(f"**Created:** {world_info.get('created_at', 'Unknown')}")
                    st.link_button("🌐 Open Marble Viewer", world_info.get('viewer_url', ''))

    with col2:
        st.markdown("### 🌐 3D World Viewer")

        # Check if there's a generated world for the selected destination
        if selected_dest in st.session_state.generated_worlds:
            world_info = st.session_state.generated_worlds[selected_dest]

            st.success(f"✨ {world_info.get('display_name', 'Destination')} generated!")

            # Show caption if available
            if world_info.get("caption"):
                with st.expander("📝 AI Description", expanded=True):
                    st.write(world_info["caption"])

            # Display panorama if available
            if world_info.get("pano_url"):
                st.markdown("#### 🖼️ 360° Panorama View")
                st.image(world_info["pano_url"], use_container_width=True)

            # Display thumbnail if available
            elif world_info.get("thumbnail"):
                st.markdown("#### 📷 World Thumbnail")
                st.image(world_info["thumbnail"], use_container_width=True)

            # Show viewer link and info
            st.markdown("---")
            st.markdown("### 🔗 Interactive 3D Viewer")

            col_a, col_b = st.columns(2)
            with col_a:
                st.link_button("🌐 Open in Marble Viewer", world_info.get('viewer_url', ''))
            with col_b:
                # Display URL for manual copying
                st.text_input("📋 Viewer URL (copy manually):", world_info.get('viewer_url', ''), key=f"url_{selected_dest}")

            st.info("""
            **💡 Tip:** The Marble Viewer link opens an interactive 3D experience where you can:
            - **Left Click + Drag**: Rotate the view
            - **Right Click + Drag**: Pan around
            - **Scroll**: Zoom in/out
            - **WASD**: Walk through the world

            *Note: The Marble Viewer may require you to be logged into World Labs.*
            """)

            # Show asset info
            with st.expander("📦 World Assets"):
                assets = world_info.get("assets", {})
                st.markdown("**Available Assets:**")
                if "thumbnail_url" in assets and assets["thumbnail_url"]:
                    st.markdown(f"- ✅ Thumbnail: Available")
                if "imagery" in assets and assets["imagery"].get("pano_url"):
                    st.markdown(f"- ✅ Panorama: Available")
                if "splats" in assets and assets["splats"].get("spz_urls"):
                    resolutions = list(assets["splats"]["spz_urls"].keys())
                    st.markdown(f"- ✅ 3D Splats: {', '.join(resolutions)}")

        else:
            # Show placeholder
            st.markdown("""
            <div class="world-card" style="text-align: center; padding: 3rem;">
                <h3>🌍 No World Generated Yet</h3>
                <p>Select a destination and click "Generate 3D World" to create an immersive experience!</p>
                <p style="color: #666; font-size: 0.9em;">
                    Powered by World Labs Marble AI
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Show example previews
            st.markdown("### 🎯 Available Destinations")
            for key, name in list(destination_names.items())[:5]:
                with st.expander(name):
                    info = TUNISIA_WORLD_PROMPTS[key]
                    st.write(info["prompt"])


# Sidebar
def render_sidebar():
    """Render the sidebar with preferences"""
    with st.sidebar:
        st.markdown("## ⚙️ Travel Preferences")

        st.session_state.preferences["destination"] = st.text_input(
            "Preferred Destination",
            value=st.session_state.preferences.get("destination", "Tunisia"),
            placeholder="e.g., Sidi Bou Said, Carthage..."
        )

        st.session_state.preferences["budget"] = st.select_slider(
            "Budget Level",
            options=["budget", "medium", "luxury"],
            value=st.session_state.preferences.get("budget", "medium")
        )

        st.markdown("### Interests")
        interests = st.multiselect(
            "What do you enjoy?",
            ["Culture & History", "Beach & Relaxation", "Adventure", "Food & Cuisine", "Nature", "Nightlife", "Shopping"],
            default=st.session_state.preferences.get("interests", [])
        )
        st.session_state.preferences["interests"] = interests

        st.session_state.preferences["days"] = st.slider(
            "Trip Duration (days)",
            min_value=1,
            max_value=14,
            value=st.session_state.preferences.get("days", 3)
        )

        st.markdown("---")

        st.markdown("### 🎯 Quick Actions")

        if st.button("🔍 Find Destinations", use_container_width=True):
            destination = st.session_state.preferences.get("destination", "Tunisia")
            prompt = f"Find destinations in {destination}"
            if st.session_state.preferences.get("budget"):
                prompt += f" for {st.session_state.preferences['budget']} budget"
            if st.session_state.preferences.get("interests"):
                interests_str = ", ".join(st.session_state.preferences["interests"])
                prompt += f" matching interests: {interests_str}"

            # Add user message and generate response
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = generate_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

        if st.button("🏨 Find Hotels", use_container_width=True):
            destination = st.session_state.preferences.get("destination", "Tunisia")
            budget = st.session_state.preferences.get("budget", "medium")
            prompt = f"Recommend hotels in {destination} for {budget} budget"

            st.session_state.messages.append({"role": "user", "content": prompt})
            response = generate_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

        if st.button("🍽️ Find Restaurants", use_container_width=True):
            destination = st.session_state.preferences.get("destination", "Tunisia")
            prompt = f"Recommend restaurants in {destination}"

            st.session_state.messages.append({"role": "user", "content": prompt})
            response = generate_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

        if st.button("📅 Create Itinerary", use_container_width=True):
            destination = st.session_state.preferences.get("destination", "Tunisia")
            days = st.session_state.preferences.get("days", 3)
            interests = ", ".join(st.session_state.preferences.get("interests", ["general"]))
            prompt = f"Create a {days}-day itinerary for {destination} focused on {interests}"

            st.session_state.messages.append({"role": "user", "content": prompt})
            response = generate_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

        if st.button("🌤️ Check Weather", use_container_width=True):
            destination = st.session_state.preferences.get("destination", "Tunis")
            prompt = f"What's the weather like in {destination}?"

            st.session_state.messages.append({"role": "user", "content": prompt})
            response = generate_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

        st.markdown("---")

        st.markdown("### 💡 Example Questions")
        examples = [
            "What are the best places to visit in Tunisia?",
            "Tell me about Sidi Bou Said",
            "Where can I find the best Tunisian food?",
            "What's the weather like in Hammamet?",
            "Convert 100 USD to TND",
            "Create a 5-day cultural itinerary"
        ]

        for example in examples:
            if st.button(example, key=example, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": example})
                response = generate_response(example)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()


# Chat interface
def render_chat():
    """Render the chat interface"""
    st.markdown("### 💬 Chat with your AI Concierge")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about travel in Tunisia..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(prompt)
                st.markdown(response)

        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


# Features section
def render_features():
    """Render feature cards"""
    st.markdown("## ✨ What can I help you with?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("#### 🗺️ Destination Discovery\n\nFind hidden gems and popular spots based on your interests and budget.")

    with col2:
        st.success("#### 📅 Trip Planning\n\nGet personalized day-by-day itineraries tailored to your preferences.")

    with col3:
        st.warning("#### 🍽️ Local Recommendations\n\nDiscover authentic restaurants, hotels, and experiences like a local.")

    col4, col5, col6 = st.columns(3)

    with col4:
        st.info("#### 🌤️ Travel Info\n\nReal-time weather updates and practical travel information.")

    with col5:
        st.success("#### 💱 Currency Help\n\nQuick currency conversion to help you budget your trip.")

    with col6:
        st.error("#### 🎬 3D World Gen\n\n**NEW!** Generate immersive 3D experiences of destinations!")


# Main app
def main():
    """Main application"""
    render_header()

    # Page navigation
    page = st.sidebar.radio(
        "Navigate",
        ["💬 AI Concierge", "🎬 3D World Generator"],
        label_visibility="collapsed"
    )

    if page == "🎬 3D World Generator":
        render_3d_worlds()
    else:
        # Layout
        col1, col2 = st.columns([1, 3])

        with col1:
            render_sidebar()

        with col2:
            # Show features if no messages
            if not st.session_state.messages:
                render_features()

                st.markdown("---")
                st.markdown("### 🚀 Get Started")
                st.markdown("Use the quick actions on the left or ask a question below to start planning your trip!")
                st.markdown("")
                st.markdown("### 🎬 Try 3D Worlds")
                st.markdown("Switch to the **3D World Generator** page to create immersive experiences!")

            render_chat()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🌍 AI Tourism Concierge | Built for ARSII AI Night Challenge</p>
        <p style="font-size: 0.9em;">Powered by LangGraph, OpenAI, Qdrant, and World Labs</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
