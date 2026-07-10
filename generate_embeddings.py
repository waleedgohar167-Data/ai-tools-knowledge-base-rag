import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_FILE = "processed_chunks.json"
OUTPUT_FILE = "embedded_chunks.json"

def get_embedding(text, model="text-embedding-3-small"):
    """Generates an embedding vector for a given text."""
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def generate_all_embeddings():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    for chunk in chunks:
        print(f"Generating embedding for chunk: {chunk['chunk_id']}...")
        chunk["embedding"] = get_embedding(chunk["chunk_text"])
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=4)
    
    print(f"Success! All embeddings saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_all_embeddings()