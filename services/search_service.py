# services/search_service.py
import os
from typing import List, Any
from openai import OpenAI
from qdrant_client import QdrantClient
from config.settings import OPENAI_API_KEY
from app_logging.logger import get_logger

logger = get_logger("Search_Service")

# 1. Initialize globally so the Rust engine stays alive and stable
openai_client = OpenAI(api_key=OPENAI_API_KEY)
db_client = QdrantClient(path="qdrant_local_data")
COLLECTION_NAME = "ai_tools_kb"

def search(query: str, limit: int = 5) -> List[Any]:
    """
    Dynamically embeds the incoming query and performs a vector search against Qdrant.
    """
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_vector = list(response.data[0].embedding)
        
        # 2. Use query_points instead of the deprecated search method
        search_result = db_client.query_points(collection_name=COLLECTION_NAME, query=query_vector, limit=limit).points  # type: ignore
        
        return search_result
    except Exception as e:
        logger.error(f"Search retrieval pipeline failed: {e}", exc_info=True)
        return []