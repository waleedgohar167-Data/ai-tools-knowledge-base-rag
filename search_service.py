import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from openai import OpenAI

# Load credentials first!
load_dotenv()

# Connect to the persistent DB
client = QdrantClient(path="qdrant_local_data")
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def search(query, limit=5):
    # Generate query embedding
    query_vec = openai_client.embeddings.create(
        input=query, 
        model="text-embedding-3-small"
    ).data[0].embedding
    
    # Search the persistent collection
    return client.query_points(
        collection_name="ai_tools_kb", 
        query=query_vec, 
        limit=limit
    ).points

if __name__ == "__main__":
    query = input("Ask a question about your AI tools: ")
    results = search(query)
    
    print("\n--- Top Results ---")
    for res in results:
        print(f"Score: {res.score:.3f} | Doc: {res.payload.get('document_name')}")
        print(f"Text: {res.payload.get('chunk_text', '')[:200]}...")
        print("-" * 30)