"""
Embedding utilities using OpenAI
"""

from openai import OpenAI
from utils.config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Get embeddings for a list of texts using OpenAI.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors
    """
    response = client.embeddings.create(
        model=Config.EMBEDDING_MODEL,
        input=texts
    )

    return [item.embedding for item in response.data]


def get_embedding(text: str) -> list[float]:
    """
    Get embedding for a single text.

    Args:
        text: Text string to embed

    Returns:
        Embedding vector
    """
    result = get_embeddings([text])
    return result[0]
