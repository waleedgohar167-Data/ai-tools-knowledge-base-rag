import json
import os
import uuid
from datetime import datetime

# Configuration
DATA_DIR = "data/sources"
OUTPUT_FILE = "processed_chunks.json"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

def chunk_text(text, size, overlap):
    """Simple word-based chunking with overlap."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i + size])
        chunks.append(chunk)
        if i + size >= len(words):
            break
    return chunks

def process_documents():
    all_chunks = []
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
                doc = json.load(f)
                
                # Combine relevant text fields for chunking
                full_text = f"{doc.get('tool_name')} {doc.get('documentation')}"
                
                # Clean text: remove extra whitespace
                clean_text = " ".join(full_text.split())
                
                chunks = chunk_text(clean_text, CHUNK_SIZE, CHUNK_OVERLAP)
                
                for chunk in chunks:
                    all_chunks.append({
                        "chunk_id": str(uuid.uuid4()),
                        "document_name": doc.get("tool_name"),
                        "source_url": doc.get("source_url"),
                        "chunk_text": chunk,
                        "timestamp": datetime.now().isoformat()
                    })
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=4)
    
    print(f"Successfully processed {len(all_chunks)} chunks into {OUTPUT_FILE}")

if __name__ == "__main__":
    process_documents()