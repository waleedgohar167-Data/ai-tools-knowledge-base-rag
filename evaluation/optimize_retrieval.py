# evaluation/optimize_retrieval.py
import time
from services.search_service import search

# 1. Define a set of diverse test queries for the RAG evaluation
TEST_QUERIES = [
    "What is the enterprise pricing for LangChain?",
    "Show me the release notes for LlamaIndex version 0.10.",
    "Explain how Cursor integrates with VS Code.",
    "What is the token limit for Anthropic Claude 3.5 Sonnet?",
    "How does Pinecone handle serverless billing?"
]

# 2. Define the Top-K limits we want to experiment with
LIMITS_TO_TEST = [3, 5, 10]

def run_optimization_experiment():
    print("=========================================================")
    print(" 🚀 Retrieval & Embedding Optimization Sweep ")
    print("=========================================================\n")
    
    for limit in LIMITS_TO_TEST:
        print(f"--- Testing Configuration: Top-K (limit) = {limit} ---")
        total_time = 0
        total_score = 0
        total_results = 0
        
        for query in TEST_QUERIES:
            start_time = time.perf_counter()
            
            # Use the existing search service you built flawlessly
            results = search(query, limit=limit)
            
            execution_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
            total_time += execution_time
            
            if results:
                # Calculate average similarity score for the returned chunks
                avg_score = sum(res.score for res in results) / len(results)
                total_score += avg_score
                total_results += 1
            
        # Calculate final metrics for this configuration
        avg_time_per_query = total_time / len(TEST_QUERIES)
        avg_overall_score = (total_score / total_results) if total_results > 0 else 0
        
        print(f"✔️ Average Processing Time: {avg_time_per_query:.2f} ms")
        print(f"✔️ Average Similarity Score: {avg_overall_score:.4f}")
        print("---------------------------------------------------------\n")
        
    print("💡 Evaluation Complete! Review the console output to determine the best limit.")
    print("Optimal enterprise standard: Choose the limit that balances >0.70 similarity with <50ms processing time.")

if __name__ == "__main__":
    run_optimization_experiment()