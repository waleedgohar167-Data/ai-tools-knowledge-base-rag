# services/query_processor.py
import json
import time
from openai import OpenAI
from config.settings import OPENAI_API_KEY
from app_logging.logger import get_logger

logger = get_logger("Query_Processor")
client = OpenAI(api_key=OPENAI_API_KEY)

def process_query_intent(raw_query: str, chat_history: list) -> dict:
    """
    Feature 10: Intelligent Pre-processing Pipeline.
    Normalizes spelling, rewrites for vector search optimization, and suggests follow-ups.
    """
    logger.info(f"Initiating intelligent query processing for: '{raw_query}'")
    
    # 1. Duplicate Query Detection
    recent_queries = [msg.get("query", "").lower().strip() for msg in chat_history if msg["role"] == "assistant"]
    is_duplicate = raw_query.lower().strip() in recent_queries
    
    if is_duplicate:
        logger.info("Duplicate query detected from recent history.")
        
    system_prompt = """
    You are an intelligent query processing engine for a technical RAG system about AI tools.
    Your job is to analyze the user's raw query and output a strict JSON object.
    
    Tasks:
    1. Check for spelling errors and correct them.
    2. Normalize and rewrite the query to make it highly optimized for vector database semantic search. Add relevant keywords if implied (e.g., if they ask about "pricing", ensure the target tool name is clearly stated).
    3. Generate exactly two highly relevant follow-up questions the user might ask next.
    
    Output JSON format:
    {
        "corrected_query": "The optimized, spelling-corrected query string",
        "suggested_followups": ["Follow-up 1", "Follow-up 2"]
    }
    """
    
    try:
        start_time = time.perf_counter()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Raw Query: {raw_query}"}
            ],
            temperature=0.1 # Low temperature for deterministic corrections
        )
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        # Enterprise-grade safety check to satisfy strict IDE linters
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("OpenAI API returned an empty or invalid choices array.")
            
        result = json.loads(response.choices[0].message.content)
        
        # Log the rewriting operation as explicitly requested in Feature 10
        logger.info(f"Query processed in {processing_time:.2f}ms | Original: '{raw_query}' | Rewritten: '{result.get('corrected_query')}'")
        
        return {
            "is_duplicate": is_duplicate,
            "optimized_query": result.get("corrected_query", raw_query),
            "suggestions": result.get("suggested_followups", [])
        }
        
    except Exception as e:
        logger.error(f"Intelligent processing failed, falling back to raw query: {e}", exc_info=True)
        return {
            "is_duplicate": is_duplicate,
            "optimized_query": raw_query,
            "suggestions": []
        }