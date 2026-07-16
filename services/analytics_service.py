from typing import Optional
import os
import json
import uuid
from config.settings import ANALYTICS_FILE
from app_logging.logger import get_logger

logger = get_logger("Analytics_Service")

# Standard estimated cost per 1,000 tokens for generation models (approximate for tracking)
COST_PER_1K_TOKENS = 0.002 

def load_analytics() -> dict:
    """Loads the current analytics from the JSON file or initializes a fresh dictionary."""
    if os.path.exists(ANALYTICS_FILE):
        try:
            with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load analytics file: {e}")
            
    return {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "total_tokens_consumed": 0,
        "estimated_api_cost_usd": 0.0,
        "cumulative_response_time_ms": 0.0,
        "cumulative_retrieval_time_ms": 0.0,
        "average_response_time_ms": 0.0,
        "average_retrieval_latency_ms": 0.0
    }

def save_analytics(data: dict):
    """Saves the analytics dictionary back to the JSON file."""
    try:
        with open(ANALYTICS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save analytics file: {e}")

def record_transaction(success: bool, retrieval_time: float = 0.0, generation_time: float = 0.0, tokens: int = 0, session_id: str = "unknown", request_id: Optional[str] = None):
    """Updates the global analytics metrics after every user request and logs session tracking."""
    # Feature 2 & Set 1 Compliance: Generate unique Request ID if not provided by the UI
    if not request_id:
        request_id = str(uuid.uuid4())

    data = load_analytics()
    
    data["total_requests"] += 1
    
    if success:
        data["successful_requests"] += 1
        data["total_tokens_consumed"] += tokens
        
        # Calculate API cost ($0.002 per 1k tokens)
        cost = (tokens / 1000.0) * COST_PER_1K_TOKENS
        data["estimated_api_cost_usd"] += cost
        
        data["cumulative_retrieval_time_ms"] += retrieval_time
        data["cumulative_response_time_ms"] += generation_time
        
        # Update Averages safely
        data["average_retrieval_latency_ms"] = data["cumulative_retrieval_time_ms"] / data["successful_requests"]
        data["average_response_time_ms"] = data["cumulative_response_time_ms"] / data["successful_requests"]
    else:
        data["failed_requests"] += 1
        
    save_analytics(data)
    
    # Feature 2 & Set 1 Compliance: Enterprise-grade logging with Request and Session IDs
    logger.info(f"Transaction logged | Req ID: {request_id} | Session: {session_id} | Success: {success} | Total Req: {data['total_requests']} | Est Cost: ${data['estimated_api_cost_usd']:.4f}")