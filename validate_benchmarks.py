import json
import time
import logging
from services.search_service import search
from services.llm_service import generate_response
from services.query_processor import process_query_intent

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def compress_context(query, results):
    """Step 2: Context Compression - removes redundant text to save tokens."""
    if not results:
        return results
    
    compressed_results = []
    query_terms = [w.lower() for w in query.split() if len(w) > 3]
    
    for res in results:
        is_dict = isinstance(res, dict)
        payload = res.get("payload", {}) if is_dict else getattr(res, "payload", {})
        text = payload.get("chunk_text", payload.get("text", ""))
        
        # Simple heuristic compression: keep sentences with keywords
        sentences = text.split(". ")
        relevant = [s for s in sentences if any(t in s.lower() for t in query_terms)]
        
        # Fallback to truncation if no exact match but vector similarity was high
        compressed_text = ". ".join(relevant) + "." if relevant else text[:300] + "..."
        
        if is_dict:
            res["payload"]["chunk_text"] = compressed_text
        else:
            res.payload["chunk_text"] = compressed_text
            
        compressed_results.append(res)
    return compressed_results

def run_validation():
    print("🚀 Starting Enterprise-Grade Benchmark Validation...\n")
    
    try:
        with open("advanced_benchmarks.json", "r", encoding="utf-8") as f:
            benchmarks = json.load(f)
    except Exception as e:
        logging.error(f"❌ JSON formatting error: {e}")
        return

    for i, test in enumerate(benchmarks, 1):
        query = test["query"]
        category = test["category"]
        
        print(f"{'-' * 50}")
        print(f"🧪 Test {i} | Category: {category}")
        print(f"🔹 Query: {query}")
        
        try:
            start_time = time.perf_counter()
            
            # Step 4 & Step 3: Input Protection & Conversation Pruning
            processed_intent = process_query_intent(query, chat_history=[])
            query_type = processed_intent.get("query_type", "NORMAL")
            top_k = processed_intent.get("recommended_top_k", 3)
            
            if query_type == "AMBIGUOUS":
                latency = (time.perf_counter() - start_time) * 1000
                print(f"⏱️ System Latency: {latency:.2f} ms")
                print("\n🤖 System Response:\nCould you please clarify what you are referring to? Your query is a bit too broad.\n")
                continue 
                
            # Step 2: Advanced Adaptive Retrieval
            sub_queries = processed_intent.get("sub_queries", [])
            results = []
            
            if query_type == "COMPLEX" and sub_queries:
                print(f"🧠 Complex Query Detected! Breaking down into {len(sub_queries)} sub-queries with Top-K={top_k}")
                for sq in sub_queries:
                    search_res = search(sq, limit=top_k)
                    res = search_res[0] if isinstance(search_res, tuple) else search_res
                    if res:
                        results.extend(res)
            else:
                optimized_query = processed_intent.get("optimized_query", query)
                search_res = search(optimized_query, limit=top_k)
                results = search_res[0] if isinstance(search_res, tuple) else search_res
            
            # Step 2: Context Compression Integration
            if results:
                original_len = len(str(results))
                results = compress_context(query, results)
                compressed_len = len(str(results))
                print(f"🗜️ Context Compressed: Size reduced from {original_len} to {compressed_len} characters.")
                print(f"📚 Context: Found {len(results)} relevant chunks.")
                gen_res = generate_response(query, results)
            else:
                print("⚠️ Context: No relevant documents found in Qdrant.")
                gen_res = generate_response(query, [])
                
            answer = gen_res[0] if isinstance(gen_res, tuple) else gen_res
            latency = (time.perf_counter() - start_time) * 1000
            
            print(f"⏱️ System Latency: {latency:.2f} ms")
            print(f"\n🤖 System Response:\n{answer}\n")
            
        except Exception as e:
            logging.error(f"❌ Pipeline Failure on Test {i}: {e}", exc_info=True)

if __name__ == "__main__":
    run_validation()