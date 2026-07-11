# ingestion/ingest.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from app_logging.logger import get_logger

logger = get_logger("Qdrant_Ingestion")
load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
db_client = QdrantClient(path="qdrant_local_data")
COLLECTION_NAME = "ai_tools_kb"
DATA_DIR = "data/sources"

def run_ultimate_ingestion():
    logger.info("Starting Direct-to-Vector Enterprise Ingestion...")
    
    if db_client.collection_exists(COLLECTION_NAME):
        db_client.delete_collection(COLLECTION_NAME)
        
    db_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    
    points = []
    
    for i, filename in enumerate(os.listdir(DATA_DIR)):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                tool_data = json.load(f)
                
            # CRITICAL FIX: Safely capture the name regardless of JSON key
            tool_name = tool_data.get("tool", tool_data.get("tool_name", tool_data.get("name", "Unknown")))
            
            doc = tool_data.get("documentation", "")
            pricing = tool_data.get("pricing", "")
            api = tool_data.get("api_docs", "")
            release = tool_data.get("release_notes", "")
            
            chunk_text = (
                f"Tool Name: {tool_name}\n"
                f"Documentation: {doc}\n"
                f"Pricing Details: {pricing}\n"
                f"API Reference: {api}\n"
                f"Release Notes & Updates: {release}\n"
            )
            
            try:
                response = openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=chunk_text
                )
                embedding = response.data[0].embedding
                
                payload = {
                    "tool": tool_name,
                    "chunk_text": chunk_text,
                    "source_url": tool_data.get("source_url", "")
                }
                
                points.append(PointStruct(id=i, vector=embedding, payload=payload))
                logger.info(f"Successfully embedded raw data for: {tool_name}")
                
            except Exception as e:
                logger.error(f"Failed embedding for {tool_name}: {e}")

    if points:
        db_client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"\n✅ SUCCESS: Ingested {len(points)} golden vectors directly into Qdrant!")
    else:
        print("\n❌ CRITICAL: No JSON files found in data/sources/")

if __name__ == "__main__":
    run_ultimate_ingestion()