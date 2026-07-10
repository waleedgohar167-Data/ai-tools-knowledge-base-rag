import json
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from openai import OpenAI
from dotenv import load_dotenv
import os
import uuid

# 1. Setup
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant = QdrantClient(":memory:") # Shared in-memory instance
COLLECTION_NAME = "ai_tools_kb"
VECTOR_SIZE = 1536 

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def initialize_and_upload():
    """Initializes collection and uploads data from embedded_chunks.json."""
    print("Initializing Qdrant and uploading data...")
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    
    with open("embedded_chunks.json", 'r', encoding='utf-8') as f:
        chunks = json.load(f)
        
    points = [
        PointStruct(
            id=i,
            vector=chunk["embedding"],
            payload={
                "document_name": chunk["document_name"],
                "chunk_text": chunk["chunk_text"]
            }
        )
        for i, chunk in enumerate(chunks)
    ]
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Successfully uploaded {len(points)} vectors.")

def search(query, limit=5):
    query_vector = get_embedding(query)
    # Using modern query_points API
    search_result = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit
    )
    return search_result.points

if __name__ == "__main__":
    # Initialize and populate memory
    initialize_and_upload()
    
    question = input("\nAsk a question about your AI tools: ")
    results = search(question)
    
    print("\n--- Top Results ---")
    for res in results:
        print(f"Score: {res.score:.4f}")
        print(f"Source: {res.payload.get('document_name', 'N/A')}")
        print(f"Text: {res.payload.get('chunk_text', 'N/A')[:200]}...")
        print("-" * 30)