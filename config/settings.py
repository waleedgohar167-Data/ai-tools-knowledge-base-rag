import os
from dotenv import load_dotenv

# Load environment variables on application startup
load_dotenv()

# ---------------------------------------------------------------------------
# Base Directory & Logging Setup
# ---------------------------------------------------------------------------
# Navigates up one level from 'config/settings.py' to reach the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure logs directory exists at startup
os.makedirs(LOG_DIR, exist_ok=True)

# Application File Paths
ANALYTICS_FILE = os.path.join(LOG_DIR, "application_analytics.json")
FEEDBACK_FILE = os.path.join(LOG_DIR, "user_feedback.csv")

# ---------------------------------------------------------------------------
# RAG Pipeline Settings
# ---------------------------------------------------------------------------
RETRIEVAL_LIMIT = 5

# ---------------------------------------------------------------------------
# Explicit External Configurations with Fail-Safes
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("CRITICAL: OPENAI_API_KEY is missing from the environment variables.")

QDRANT_PATH = os.getenv("QDRANT_PATH", "qdrant_local_data")
DATA_DIR = os.getenv("DATA_DIR", "data")