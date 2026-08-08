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
    Intelligent Pre-processing Pipeline, Query Decomposition & Conversation Pruning.
    """
    logger.info(f"Initiating intelligent query processing for: '{raw_query}'")
    
    clean_raw = raw_query.strip()
    
    # STEP 3: Conversation Intelligence (Pruning)
    # Keep only the last 4 messages to prevent token bloat
    pruned_history = chat_history[-4:] if len(chat_history) > 4 else chat_history
    
    if not clean_raw:
        return {
            "is_duplicate": False,
            "optimized_query": "",
            "query_type": "NORMAL",
            "sub_queries": [],
            "recommended_top_k": 3,
            "suggestions": []
        }
    
    # Enhanced Duplicate Query Detection
    is_duplicate = False
    clean_lower = clean_raw.lower()
    for msg in pruned_history:
        prev_q = msg.get("query") or (msg.get("content") if msg.get("role") == "user" else None)
        if prev_q and str(prev_q).lower().strip() == clean_lower:
            is_duplicate = True
            break
            
    system_prompt = """You are an intelligent query processing engine for a technical RAG system about AI tools.
Analyze the user's raw query and output a strict JSON object.

Tasks:
1. Classify the query_type: 'AMBIGUOUS', 'COMPLEX', or 'NORMAL'.
2. Rewrite the query to optimize semantic vector retrieval.
3. If COMPLEX, break it down into 2-3 simpler 'sub_queries'. Otherwise, empty array.
4. Determine 'recommended_top_k': 5 for COMPLEX, 3 for NORMAL, 0 for AMBIGUOUS.
5. Generate exactly two highly relevant follow-up questions.

Output JSON format:
{
    "query_type": "NORMAL",
    "corrected_query": "The optimized query",
    "sub_queries": ["sub_query_1"],
    "recommended_top_k": 3,
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
            temperature=0.1
        )
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        # Defensive check to prevent the 'NoneType' strip error
        if not response.choices or not response.choices[0].message.content:
            raise ValueError("OpenAI API returned an empty or invalid choices array.")
            
        raw_content = response.choices[0].message.content.strip()
        result = json.loads(raw_content)
        
        optimized_query = result.get("corrected_query", clean_raw)
        query_type = result.get("query_type", "NORMAL")
        sub_queries = result.get("sub_queries", [])
        recommended_top_k = result.get("recommended_top_k", 3)
        suggestions = result.get("suggested_followups", [])
        
        return {
            "is_duplicate": is_duplicate,
            "optimized_query": optimized_query,
            "query_type": query_type,
            "sub_queries": sub_queries,
            "recommended_top_k": recommended_top_k,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Intelligent processing failed, falling back to raw query: {e}", exc_info=True)
        return {
            "is_duplicate": is_duplicate,
            "optimized_query": clean_raw,
            "query_type": "NORMAL",
            "sub_queries": [],
            "recommended_top_k": 3,
            "suggestions": []
        }