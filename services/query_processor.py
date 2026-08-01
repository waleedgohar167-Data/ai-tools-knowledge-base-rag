# services/query_processor.py
import json
import time
from typing import Dict, Any, List
from openai import OpenAI
from config.settings import OPENAI_API_KEY
from app_logging.logger import get_logger

logger = get_logger("Query_Processor")
client = OpenAI(api_key=OPENAI_API_KEY)

def process_query_intent(raw_query: str, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Feature 10: Intelligent Pre-processing Pipeline.
    Normalizes spelling, optimizes queries for vector search retrieval, detects duplicates,
    and generates contextual follow-up suggestions.
    
    Returns a dictionary with:
      - is_duplicate (bool)
      - optimized_query (str)
      - suggestions (List[str])
    """
    logger.info(f"Initiating intelligent query processing for: '{raw_query}'")
    
    clean_raw = raw_query.strip()
    if not clean_raw:
        return {
            "is_duplicate": False,
            "optimized_query": "",
            "suggestions": []
        }
    
    # 1. Enhanced Duplicate Query Detection across history objects
    is_duplicate = False
    clean_lower = clean_raw.lower()
    for msg in chat_history:
        prev_q = msg.get("query") or (msg.get("content") if msg.get("role") == "user" else None)
        if prev_q and str(prev_q).lower().strip() == clean_lower:
            is_duplicate = True
            break
            
    if is_duplicate:
        logger.info("Duplicate query detected from recent session history.")
        
    system_prompt = """You are an intelligent query processing engine for a technical RAG system about AI tools.
Analyze the user's raw query and output a strict JSON object.

Tasks:
1. Check for spelling errors and normalize technical terminology.
2. Rewrite the query to optimize semantic vector retrieval (ensure relevant AI tool names or context keywords are clear).
3. Generate exactly two highly relevant follow-up questions the user might ask next.

Output JSON format:
{
    "corrected_query": "The optimized, spelling-corrected query string",
    "suggested_followups": ["Follow-up 1", "Follow-up 2"]
}"""

    try:
        start_time = time.perf_counter()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Raw Query: {clean_raw}"}
            ],
            temperature=0.1  # Low temperature for deterministic corrections
        )
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        # Defensive check for choice payload safety
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("OpenAI API returned an empty or invalid choices array.")
            
        raw_content = response.choices[0].message.content.strip()
        result = json.loads(raw_content)
        
        # Extract and validate fields
        optimized_query = result.get("corrected_query", clean_raw)
        if not isinstance(optimized_query, str) or not optimized_query.strip():
            optimized_query = clean_raw
            
        suggestions = result.get("suggested_followups", [])
        if not isinstance(suggestions, list):
            suggestions = []
            
        logger.info(f"Query processed in {processing_time:.2f}ms | Original: '{clean_raw}' | Rewritten: '{optimized_query}'")
        
        return {
            "is_duplicate": is_duplicate,
            "optimized_query": optimized_query,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Intelligent processing failed, falling back to raw query: {e}", exc_info=True)
        return {
            "is_duplicate": is_duplicate,
            "optimized_query": clean_raw,
            "suggestions": []
        }