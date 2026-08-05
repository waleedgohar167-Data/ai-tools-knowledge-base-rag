import json
from services.search_service import search
from services.llm_service import generate_response

def run_validation():
    print("🚀 Starting Advanced Benchmark Validation...\n")
    
    try:
        with open("advanced_benchmarks.json", "r", encoding="utf-8") as f:
            benchmarks = json.load(f)
    except FileNotFoundError:
        print("❌ Error: advanced_benchmarks.json not found.")
        return

    for i, test in enumerate(benchmarks, 1):
        query = test["query"]
        expected = test["expected_behavior"]
        category = test["category"]
        
        print(f"{"-" * 40}")
        print(f"🧪 Test {i} | Category: {category}")
        print(f"🔹 Query: {query}")
        print(f"🎯 Expected: {expected}")
        
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
        
        print(f"\n🤖 System Response:\n{answer}\n")

if __name__ == "__main__":
    run_validation()