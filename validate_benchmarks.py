import json
import time
import logging
from services.search_service import search
from services.llm_service import generate_response

# Phase 4 Optimization: Set up production-level logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def run_validation():
    print("🚀 Starting Enterprise-Grade Benchmark Validation...\n")
    
    try:
        with open("advanced_benchmarks.json", "r", encoding="utf-8") as f:
            benchmarks = json.load(f)
    except FileNotFoundError:
        logging.error("❌ Error: advanced_benchmarks.json not found.")
        return
    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON formatting error: {e}")
        return

    for i, test in enumerate(benchmarks, 1):
        query = test["query"]
        expected = test.get("expected_behavior", "Unknown")
        category = test["category"]
        
        print(f"{'-' * 50}")
        print(f"🧪 Test {i} | Category: {category}")
        print(f"🔹 Query: {query}")
        print(f"🎯 Expected: {expected}")
        
        try:
            # Track latency to monitor API optimization
            start_time = time.perf_counter()
            
            # 1. Retrieve Context from your Vector DB
            search_res = search(query, limit=3)
            results = search_res[0] if isinstance(search_res, tuple) else search_res
            
            # 2. Generate Response
            if not results:
                print("⚠️ Context: No relevant documents found in Qdrant.")
                gen_res = generate_response(query, [])
            else:
                print(f"📚 Context: Found {len(results)} relevant chunks.")
                gen_res = generate_response(query, results)
                
            answer = gen_res[0] if isinstance(gen_res, tuple) else gen_res
            
            # Calculate and display execution time
            latency = (time.perf_counter() - start_time) * 1000
            
            print(f"⏱️ System Latency: {latency:.2f} ms")
            print(f"\n🤖 System Response:\n{answer}\n")
            
        except Exception as e:
            # Prevents a single test failure from crashing the entire benchmark suite
            logging.error(f"❌ Pipeline Failure on Test {i}: {e}", exc_info=True)

if __name__ == "__main__":
    run_validation()