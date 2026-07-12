# services/search_service.py
import os
import time
from typing import List, Any, Tuple
from openai import OpenAI
from qdrant_client import QdrantClient
from config.settings import OPENAI_API_KEY
from app_logging.logger import get_logger

logger = get_logger("Search_Service")

logger.info("Initializing global QdrantClient and OpenAI embedding engine.")
openai_client = OpenAI(api_key=OPENAI_API_KEY)
db_client = QdrantClient(path="qdrant_local_data")
COLLECTION_NAME = "ai_tools_kb"

def search(query: str, limit: int = 5) -> Tuple[List[Any], float]:
    """
    Dynamically embeds the incoming query and performs a vector search against Qdrant.
    Returns the search results and the retrieval latency in ms.
    """
    start_time = time.perf_counter()
    logger.info(f"Initiating vector retrieval for query: '{query}'")
    
    try:
        logger.info("Sending request to OpenAI for text embeddings.")
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_vector = list(response.data[0].embedding)
        
        logger.info(f"Querying Qdrant vector database (Collection: {COLLECTION_NAME}, Limit: {limit}).")
        search_result = db_client.query_points(
            collection_name="ai_tools_kb", 
            query=query_vector, 
            limit=limit
        ).points  # type: ignore
        
        retrieval_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Successfully retrieved {len(search_result)} documents in {retrieval_time:.2f} ms.")
        
        return search_result, retrieval_time
    except Exception as e:
        logger.error(f"Search retrieval pipeline failed: {e}", exc_info=True)
        return [], 0.0