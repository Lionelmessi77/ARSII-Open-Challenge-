"""
Qdrant Vector Database Manager
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional
from utils.config import Config
from utils.embeddings import get_embedding


class QdrantManager:
    """Manages Qdrant vector database operations"""

    def __init__(self):
        Config.validate()
        self.client = QdrantClient(
            url=Config.QDRANT_URL,
            api_key=Config.QDRANT_API_KEY
        )

    def create_collection(self, collection_name: str):
        """Create a new collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        existing = [c.name for c in collections]

        if collection_name not in existing:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=Config.EMBEDDING_DIMENSIONS,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {collection_name}")
        else:
            print(f"Collection already exists: {collection_name}")

    def add_points(self, collection_name: str, points: List[Dict]):
        """
        Add points to a collection.

        Args:
            collection_name: Name of the collection
            points: List of dicts with 'id', 'text', and optional 'metadata'
        """
        vectors = []
        for point in points:
            text = point.get("text", "")
            embedding = get_embedding(text)
            vectors.append({
                "id": point["id"],
                "vector": embedding,
                "payload": {**point.get("metadata", {}), "text": text}
            })

        # Convert to PointStruct
        points_struct = [
            PointStruct(
                id=v["id"],
                vector=v["vector"],
                payload=v["payload"]
            )
            for v in vectors
        ]

        self.client.upsert(collection_name=collection_name, points=points_struct)

    def search(
        self,
        collection_name: str,
        query_text: str,
        limit: int = 5,
        score_threshold: float = 0.5,
        filter: Optional[Dict] = None
    ) -> List:
        """
        Search a collection by query text.

        Args:
            collection_name: Name of the collection
            query_text: Search query
            limit: Max results
            score_threshold: Minimum similarity score
            filter: Optional metadata filter

        Returns:
            List of search results
        """
        query_vector = get_embedding(query_text)

        search_filter = None
        if filter:
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filter.items()
            ]
            search_filter = Filter(must=conditions)

        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=search_filter
        )

        return results

    def get_all_points(self, collection_name: str) -> List[Dict]:
        """Get all points from a collection"""
        results = self.client.scroll(
            collection_name=collection_name,
            limit=1000,
            with_payload=True
        )

        points = []
        for point in results[0]:
            points.append({
                "id": point.id,
                "payload": point.payload
            })

        return points

    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        self.client.delete_collection(collection_name=collection_name)
        print(f"Deleted collection: {collection_name}")

    def init_collections(self):
        """Initialize all required collections"""
        for name, description in Config.COLLECTIONS.items():
            self.create_collection(name)


# Initialize collections on module import
def init_database():
    """Initialize the vector database with all collections"""
    manager = QdrantManager()
    manager.init_collections()
    return manager
