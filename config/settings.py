import os
from dotenv import load_dotenv

# Load environment variables on application startup
load_dotenv()

# Explicitly define configurations with fail-safes
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("CRITICAL: OPENAI_API_KEY is missing from the environment variables.")

QDRANT_PATH = os.getenv("QDRANT_PATH", "qdrant_local_data")
DATA_DIR = os.getenv("DATA_DIR", "data")