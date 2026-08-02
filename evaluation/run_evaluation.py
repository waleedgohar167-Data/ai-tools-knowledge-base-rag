# evaluation/run_evaluation.py
import json
import os
import time
from services.search_service import search
from services.llm_service import generate_response, evaluate_response_quality
from evaluation.metrics import calculate_hit_rate, calculate_average_metric, calculate_mrr
from app_logging.logger import get_logger

# Initialize our centralized application logging
logger = get_logger("Evaluation_Framework")

# Pointing explicitly to the consolidated 'evaluation' directory
QUERY_FILE = os.path.join("evaluation", "test_queries.json")

def load_test_queries():
    if not os.path.exists(QUERY_FILE):
        logger.error(f"❌ Error: Could not find '{QUERY_FILE}'.")
        return []
    with open(QUERY_FILE, "r") as f:
        data = json.load(f)
        return data.get("queries", [])

def run_enterprise_evaluation():
    DATASET = load_test_queries()
    
    if not DATASET:
        print(f"❌ No queries loaded. Please ensure {QUERY_FILE} exists.")
        return

    print("=========================================================")
    print(" 🚀 Running Automated AI Evaluation Framework Pipeline   ")
    print(f" 🔥 Total Benchmark Queries Loaded: {len(DATASET)}      ")
    print("=========================================================\n")
    
    total_retrieval_time = 0
    total_llm_time = 0
    total_tokens = 0
    hit_count = 0
    hits_at_1 = 0
    hits_at_3 = 0
    total_mrr = 0.0
    
    report_lines = ["# Enterprise AI Performance Report\n"]
    structured_evaluation_data = []

    for i, item in enumerate(DATASET, 1):
        query = item["query"]
        # Handle both JSON formats (expected_tool from JSON, or expected_source from older code)
        expected = item.get("expected_tool", item.get("expected_source", ""))
        expected_answer = item.get("expected_answer", "N/A - Evaluated dynamically via LLM Judge")
        
        print(f"🔄 Testing [{i}/{len(DATASET)}]: \"{query}\"")
        
        # 1. Evaluate Semantic Retrieval Performance
        start_retrieval = time.perf_counter()
        search_res = search(query, limit=5)
        
        # Safely unpack search response (results, latency) so it doesn't break
        if isinstance(search_res, tuple):
            results, retrieval_time = search_res[0], search_res[1]
        else:
            results = search_res
            retrieval_time = (time.perf_counter() - start_retrieval) * 1000
            
        total_retrieval_time += retrieval_time
        
        retrieved_docs = []
        citations = []
        if results:
            for res in results:
                payload = getattr(res, 'payload', {}) or {}
                # Handle either dicts or Qdrant PointStructs defensively
                if isinstance(res, dict):
                    payload = res.get('payload', {})
                tool_name = payload.get('tool', payload.get('document_name', 'Unknown Document'))
                source_url = payload.get('source_url', 'No Source Link')
                retrieved_docs.append(tool_name)
                citations.append(f"`{tool_name}` ({source_url})")
        
        # Evaluate strict ranks for Hit Rate @ 1 and Hit Rate @ 3
        rank = 0
        for rank_idx, doc_name in enumerate(retrieved_docs, 1):
            if expected.lower() in doc_name.lower():
                rank = rank_idx
                break
                
        if rank == 1:
            hits_at_1 += 1
            hits_at_3 += 1
            hit_count += 1
        elif 1 < rank <= 3:
            hits_at_3 += 1
            hit_count += 1
        elif rank > 3:
            hit_count += 1
            
        # Continue using your custom MRR calculator
        query_mrr = calculate_mrr(retrieved_docs, expected)
        total_mrr += query_mrr
        
        # 2. Evaluate LLM Generation Performance
        answer, llm_time, tokens = generate_response(query, results)
        total_llm_time += llm_time
        total_tokens += tokens
        
        # Format the context strictly for the Judge
        context_string = "\n".join([
            getattr(res, 'payload', {}).get('text', '') if not isinstance(res, dict) else res.get('payload', {}).get('text', '') 
            for res in results
        ])
        
        # 3. LLM-as-a-Judge Evaluation
        print(f"   -> Judging response quality...")
        llm_scores = evaluate_response_quality(query, context_string, answer)
        
        # Append structured data for JSON Export
        structured_evaluation_data.append({
            "query": query,
            "expected_source": expected,
            "expected_answer": expected_answer,
            "retrieval_hit": (rank > 0),
            "rank_found": rank,
            "mrr": query_mrr,
            "latency": {"retrieval_ms": retrieval_time, "generation_ms": llm_time},
            "tokens_used": tokens,
            "judge_scores": llm_scores,
            "generated_response": answer
        })
        
        # Build Markdown report logs
        report_lines.append(f"### Query {i}: {query}")
        report_lines.append(f"- **Expected Target Source:** `{expected}`")
        report_lines.append(f"- **Retrieval Hit Accuracy:** {'✅ PASS' if rank > 0 else '❌ FAIL'} ({retrieval_time:.2f} ms)")
        report_lines.append(f"- **Reciprocal Rank (RR):** `{query_mrr:.4f}`")
        report_lines.append(f"- **Source Citations (Top-K):** {', '.join(citations) if citations else 'None'}")
        report_lines.append(f"- **LLM Generation Latency:** {llm_time:.2f} ms")
        report_lines.append(f"- **Approximate Token Consumption:** ~{tokens} tokens")
        
        report_lines.append(f"- **LLM Evaluation Scores:**")
        report_lines.append(f"  - Answer Relevance: {llm_scores.get('answer_relevance', 0)}/5")
        report_lines.append(f"  - Context Faithfulness: {llm_scores.get('context_faithfulness', 0)}/5")
        report_lines.append(f"  - Completeness: {llm_scores.get('completeness', 0)}/5")
        report_lines.append(f"  - Correctness: {llm_scores.get('correctness', 0)}/5")
        report_lines.append(f"  - Clarity: {llm_scores.get('clarity', 0)}/5")
        report_lines.append(f"  - Source Citation Quality: {llm_scores.get('source_citation_quality', 0)}/5")
        
        report_lines.append(f"- **Generated Response Preview:**\n> {answer[:200].replace('\n', ' ')}...\n")

    # 4. Compute Aggregated Global Metrics
    avg_retrieval = calculate_average_metric(total_retrieval_time, len(DATASET))
    avg_llm = calculate_average_metric(total_llm_time, len(DATASET))
    avg_tokens = total_tokens / len(DATASET)
    final_hit_rate = calculate_hit_rate(hit_count, len(DATASET))
    final_mrr = calculate_average_metric(total_mrr, len(DATASET))
    
    hit_rate_at_1 = (hits_at_1 / len(DATASET)) * 100
    hit_rate_at_3 = (hits_at_3 / len(DATASET)) * 100
    
    # Prepend the high-level Executive Summary
    report_lines.insert(1, f"## Executive Summary Performance Metrics")
    report_lines.insert(2, f"- **Total System Queries Evaluated:** {len(DATASET)}")
    report_lines.insert(3, f"- **Overall Hit Rate:** {final_hit_rate:.2f}%")
    report_lines.insert(4, f"- **Hit Rate @ 1:** {hit_rate_at_1:.2f}%")
    report_lines.insert(5, f"- **Hit Rate @ 3:** {hit_rate_at_3:.2f}%")
    report_lines.insert(6, f"- **Mean Reciprocal Rank (MRR):** {final_mrr:.4f}")
    report_lines.insert(7, f"- **Average Retrieval Latency:** {avg_retrieval:.2f} ms")
    report_lines.insert(8, f"- **Average Generation Latency:** {avg_llm:.2f} ms")
    report_lines.insert(9, f"- **Average Tokens Used:** {avg_tokens:.1f}\n")
    report_lines.insert(10, f"---")
    
    # Save Markdown File
    try:
        with open("evaluation_report.md", "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
    except Exception as e:
        logger.error(f"Failed to write markdown evaluation report: {e}", exc_info=True)

    # Save JSON File (Step 4 Fulfillment)
    try:
        OUTPUT_FILE = os.path.join("evaluation", "results.json")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "summary": {
                    "total_queries": len(DATASET),
                    "hit_rate_at_1": hit_rate_at_1,
                    "hit_rate_at_3": hit_rate_at_3,
                    "mrr": final_mrr,
                    "avg_retrieval_ms": avg_retrieval,
                    "avg_generation_ms": avg_llm,
                    "avg_tokens": avg_tokens
                },
                "details": structured_evaluation_data
            }, f, indent=4)
        print(f"\n✅ Structured JSON evaluation data saved to '{OUTPUT_FILE}'")
    except Exception as e:
        logger.error(f"Failed to save JSON results: {e}", exc_info=True)

    print("============ Evaluation Metrics Summary ============")
    print(f"🎯 Hit Rate @ 1: {hit_rate_at_1:.2f}%")
    print(f"🎯 Hit Rate @ 3: {hit_rate_at_3:.2f}%")
    print(f"📊 Mean Reciprocal Rank (MRR): {final_mrr:.4f}")
    print(f"⚡ Avg Retrieval Time: {avg_retrieval:.2f} ms")
    print(f"⚡ Avg Generation Time: {avg_llm:.2f} ms")
    print(f"🔢 Avg Tokens Used: {avg_tokens:.1f}")
    print("====================================================")
    print(f"✅ Compliance check complete! Execution successfully evaluated {len(DATASET)} records.")

if __name__ == "__main__":
    run_enterprise_evaluation()