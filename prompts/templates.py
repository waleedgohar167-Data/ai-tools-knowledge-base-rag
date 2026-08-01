# prompts/templates.py
from typing import List, Any, Tuple

def detect_intent(user_query: str) -> str:
    """Simple intent router to select the best enterprise prompt template."""
    query = user_query.lower()
    if any(word in query for word in ["compare", "vs", "difference", "better"]):
        return "comparison"
    elif any(word in query for word in ["summar", "overview", "brief"]):
        return "summary"
    elif any(word in query for word in ["api", "endpoint", "code", "function"]):
        return "api"
    else:
        return "general"

def build_rag_prompt(user_query: str, search_results: List[Any]) -> Tuple[str, str]:
    """
    Constructs the strictly bounded system prompt and user context for RAG generation.
    Routes to specific templates based on the user's intent.
    """
    context = ""
    for res in search_results:
        payload = res.payload or {}
        # Safely using the exact 'tool' and 'chunk_text' keys from your dlt pipeline schema
        doc_name = payload.get('tool', 'Unknown Document')
        text = payload.get('chunk_text', '')
        
        # ELITE FEATURE: Safely expose the Qdrant match score to the LLM context if it exists
        score_str = f" | Match Score: {res.score:.4f}" if hasattr(res, 'score') and res.score is not None else ""
        
        context += f"--- [Source Document: {doc_name}{score_str}] ---\nContent: {text}\n\n"

    intent = detect_intent(user_query)
    
    # Phase 5: Upgraded Guardrails for zero-hallucination and strict source attribution
    base_guardrails = (
        "Strict Directives:\n"
        "1. Answer EXCLUSIVELY using the provided Context Documents.\n"
        "2. If the context does not contain the answer, say EXACTLY: 'I do not have enough information to answer that based on the current knowledge base.'\n"
        "3. Never hallucinate, guess, or use outside knowledge.\n"
        "4. Always explicitly cite the tool name in bold (e.g., **LangChain**) when referencing its capabilities, pricing, or APIs.\n"
        "5. Always structure your response professionally.\n"
    )

    # Phase 5: Separate Prompt Templates
    if intent == "general":
        system_prompt = "You are an elite AI Technical Assistant.\n\n" + base_guardrails + "\nFormat your response cleanly. Include a 'Summary' section and a 'Key Points' bulleted list."
    
    elif intent == "comparison":
        system_prompt = "You are an elite AI Technical Analyst.\n\n" + base_guardrails + "\nFormat your response as a structured comparison. Use a Markdown table to highlight differences and similarities clearly."
    
    elif intent == "summary":
        system_prompt = "You are an elite AI Executive Summarizer.\n\n" + base_guardrails + "\nFormat your response as a high-level executive summary. Provide a 'TL;DR' at the top, followed by 'Core Takeaways'."
    
    elif intent == "api":
        system_prompt = "You are an elite AI Developer Advocate.\n\n" + base_guardrails + "\nFormat your response specifically for a developer. Highlight API endpoints, parameters, and include clean code blocks."

    user_prompt = f"Context Documents:\n{context}\nUser Question: {user_query}"
    
    return system_prompt, user_prompt