"""
Configuration management for Tourism Concierge
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Qdrant
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_URL = os.getenv("QDRANT_URL")

    # Model settings
    EMBEDDING_MODEL = "text-embedding-3-small"
    CHAT_MODEL = "gpt-4o-mini"

    # Vector DB settings
    COLLECTIONS = {
        "destinations": "Tourist destinations with descriptions",
        "attractions": "Points of interest, attractions, sites",
        "restaurants": "Restaurant recommendations",
        "hotels": "Hotel and accommodation options"
    }

    # Embedding dimensions
    EMBEDDING_DIMENSIONS = 1536  # for text-embedding-3-small

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not cls.QDRANT_API_KEY:
            missing.append("QDRANT_API_KEY")
        if not cls.QDRANT_URL:
            missing.append("QDRANT_URL")

        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")

        return True
