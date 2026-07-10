import json
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

load_dotenv()
# Persistent storage: folder 'qdrant_local_data'
client = QdrantClient(path="qdrant_local_data")
COLLECTION_NAME = "ai_tools_kb"

def run_ingestion():
    # Clean/Reset collection for a fresh professional start
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    
    # Load your DLT-collected datasets
    # Assumes your cleaned DLT data is in embedded_chunks.json
    with open("embedded_chunks.json", 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    points = [
        PointStruct(id=i, vector=c["embedding"], payload=c) 
        for i, c in enumerate(chunks)
    ]
    
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Successfully ingested {len(points)} vectors into persistent storage.")
    client.close()

if __name__ == "__main__":
    run_ingestion()