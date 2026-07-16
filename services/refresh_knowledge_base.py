# services/refresh_knowledge_base.py
import os
import hashlib
import json
from app_logging.logger import get_logger

logger = get_logger("Incremental_Ingestion")

# Configuration
DATA_DIRECTORY = "data/documents"  # Point this to where your PDFs/Text files live
STATE_FILE = "ingestion_state.json"

def get_file_hash(filepath: str) -> str:
    """Generates an MD5 hash of a file to detect if it has changed."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            # Read in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Failed to hash file {filepath}: {e}")
        return ""

def load_ingestion_state() -> dict:
    """Loads the history of previously ingested file hashes."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_ingestion_state(state: dict):
    """Saves the updated file hashes to disk."""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

def run_automatic_refresh():
    """
    Feature 9 Pipeline: Scans directory, skips duplicates, and processes new files.
    """
    logger.info("Starting Automatic Knowledge Base Refresh cycle...")
    
    if not os.path.exists(DATA_DIRECTORY):
        logger.warning(f"Data directory '{DATA_DIRECTORY}' not found. Aborting refresh.")
        return

    state = load_ingestion_state()
    new_files_processed = 0
    skipped_files = 0

    for filename in os.listdir(DATA_DIRECTORY):
        filepath = os.path.join(DATA_DIRECTORY, filename)
        
        # Skip directories, only process files
        if not os.path.isfile(filepath):
            continue
            
        file_hash = get_file_hash(filepath)
        
        # Duplicate Detection Logic
        if filename in state and state[filename] == file_hash:
            logger.debug(f"Skipping duplicate/unchanged file: {filename}")
            skipped_files += 1
            continue
            
        logger.info(f"New or modified file detected: {filename}. Processing embeddings...")
        
        try:
            # ========================================================
            # TODO: Call your specific document loader / embedding function here
            # Example:
            # chunks = load_and_chunk_document(filepath)
            # vector_db.add_documents(chunks)
            # ========================================================
            
            # If embedding succeeds, update the state ledger
            state[filename] = file_hash
            new_files_processed += 1
            logger.info(f"Successfully updated embeddings for {filename}")
            
        except Exception as e:
            logger.error(f"Failed to ingest {filename}: {e}", exc_info=True)

    save_ingestion_state(state)
    logger.info(f"Refresh cycle complete. Processed {new_files_processed} new files. Skipped {skipped_files} duplicates.")

if __name__ == "__main__":
    run_automatic_refresh()