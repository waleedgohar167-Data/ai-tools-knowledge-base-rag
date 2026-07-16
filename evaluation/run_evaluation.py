# evaluation/run_evaluation.py
import json
import time
from services.search_service import search
from services.llm_service import generate_response, evaluate_response_quality
from evaluation.metrics import calculate_hit_rate, calculate_average_metric, calculate_mrr
from app_logging.logger import get_logger

# Initialize our centralized application logging
logger = get_logger("Evaluation_Framework")

# 20 Test Questions with Expected Source AND Expected Answer
DATASET = [
    # --- LangChain ---
    {"query": "What is the enterprise pricing for LangChain?", "expected_source": "LangChain", "expected_answer": "LangChain offers enterprise pricing customized per organization; you must contact sales for a specific quote."},
    {"query": "How does LangChain handle vector store abstractions?", "expected_source": "LangChain", "expected_answer": "LangChain provides standard interfaces to wrap various vector databases, allowing seamless switching between them."},
    {"query": "Give me an example of a LangChain expression language LCEL chain.", "expected_source": "LangChain", "expected_answer": "An LCEL chain typically links a prompt template, an LLM, and an output parser using the pipe (|) operator."},
    {"query": "What are the latest production release notes for LangChain?", "expected_source": "LangChain", "expected_answer": "The latest notes include improved async support, LCEL performance enhancements, and expanded tracing capabilities."},
    
    # --- Cursor ---
    {"query": "Explain how Cursor integrates with VS Code.", "expected_source": "Cursor", "expected_answer": "Cursor is a fork of VS Code, meaning it natively supports all VS Code extensions, keybindings, and settings."},
    {"query": "What are the indexing capabilities of Cursor for large codebases?", "expected_source": "Cursor", "expected_answer": "Cursor builds a local semantic index of your codebase to allow the AI to understand cross-file context and dependencies."},
    {"query": "Does Cursor support multi-line editing using AI commands?", "expected_source": "Cursor", "expected_answer": "Yes, Cursor's Cmd-K feature allows AI-driven multi-line edits and refactoring directly inline."},
    {"query": "What is the pricing model for Cursor Pro and Business tiers?", "expected_source": "Cursor", "expected_answer": "Cursor Pro is $20/month, and Business is $40/user/month with enhanced privacy and central billing."},
    
    # --- Pinecone ---
    {"query": "Compare Pinecone and ChromaDB pricing.", "expected_source": "Pinecone", "expected_answer": "Pinecone is a managed SaaS with consumption-based pricing, whereas ChromaDB is open-source and free to host yourself."},
    {"query": "What is the architecture behind Pinecone serverless indexes?", "expected_source": "Pinecone", "expected_answer": "Serverless Pinecone separates compute and storage, scaling automatically based on usage without manual pod provisioning."},
    {"query": "How does Pinecone handle multi-tenant vector isolation?", "expected_source": "Pinecone", "expected_answer": "Pinecone uses Namespaces to partition vectors within a single index, ensuring isolated multi-tenant data retrieval."},
    {"query": "What is the maximum vector dimension supported by Pinecone?", "expected_source": "Pinecone", "expected_answer": "Pinecone currently supports up to 20,000 dimensions for dense vectors."},
    
    # --- Anthropic Claude ---
    {"query": "What is the token limit for Anthropic Claude 3.5 Sonnet?", "expected_source": "Anthropic Claude", "expected_answer": "Claude 3.5 Sonnet features a massive 200,000 token context window."},
    {"query": "How do Anthropic Claude artifacts work in a development workflow?", "expected_source": "Anthropic Claude", "expected_answer": "Artifacts are standalone, interactive UI elements (like code, charts, or SVG) generated in a dedicated panel next to the chat."},
    {"query": "What are the specific fine-tuning parameters for Claude models?", "expected_source": "Anthropic Claude", "expected_answer": "Anthropic generally does not offer traditional self-serve fine-tuning; they focus on prompt engineering and constitutional AI."},
    {"query": "Compare the cost per million tokens for Claude 3.5 Sonnet vs Opus.", "expected_source": "Anthropic Claude", "expected_answer": "Sonnet is significantly cheaper at $3/M input and $15/M output, while Opus is $15/M input and $75/M output."},
    
    # --- LlamaIndex ---
    {"query": "Summarize what LlamaIndex does for RAG pipelines.", "expected_source": "LlamaIndex", "expected_answer": "LlamaIndex acts as a data framework to connect custom data sources to LLMs, providing advanced routing, parsing, and query engines."},
    {"query": "How do you build a hierarchical node parser in LlamaIndex?", "expected_source": "LlamaIndex", "expected_answer": "You use the HierarchicalNodeParser class to split documents into larger chunks (parent nodes) and smaller chunks (child nodes)."},
    {"query": "What vector database integrations are supported natively by LlamaIndex?", "expected_source": "LlamaIndex", "expected_answer": "It supports dozens of databases including Qdrant, Pinecone, Chroma, Milvus, and Weaviate."},
    {"query": "Explain property graph indexes in LlamaIndex framework.", "expected_source": "LlamaIndex", "expected_answer": "Property Graph Indexes extract entities and relationships from text to build a knowledge graph, enhancing complex reasoning queries."}
]

def run_enterprise_evaluation():
    print("=========================================================")
    print(" 🚀 Running Automated AI Evaluation Framework Pipeline   ")
    print(f" 🔥 Total Benchmark Queries Loaded: {len(DATASET)}      ")
    print("=========================================================\n")
    
    total_retrieval_time = 0
    total_llm_time = 0
    hit_count = 0
    total_mrr = 0.0
    
    report_lines = ["# Enterprise AI Performance Report\n"]
    
    #  Array to store structured JSON data
    structured_evaluation_data = []
    
    # Test the System on at least 10 sample questions
    test_subset = DATASET[:10]

    for i, item in enumerate(test_subset, 1):
        query = item["query"]
        expected = item["expected_source"]
        expected_answer = item["expected_answer"]
        print(f"🔄 Testing [{i}/{len(test_subset)}]: \"{query}\"")
        
        # 1. Evaluate Semantic Retrieval Performance
        results, retrieval_time = search(query, limit=5)
        total_retrieval_time += retrieval_time
        
        retrieved_docs = []
        citations = []
        if results:
            for res in results:
                payload = getattr(res, 'payload', {}) or {}
                tool_name = payload.get('tool', payload.get('document_name', 'Unknown Document'))
                source_url = payload.get('source_url', 'No Source Link')
                retrieved_docs.append(tool_name)
                citations.append(f"`{tool_name}` ({source_url})")
        
        hit = any(expected.lower() in doc.lower() for doc in retrieved_docs)
        if hit:
            hit_count += 1
            
        query_mrr = calculate_mrr(retrieved_docs, expected)
        total_mrr += query_mrr
        
        # 2. Evaluate LLM Generation Performance
        answer, llm_time, tokens = generate_response(query, results)
        total_llm_time += llm_time
        
        # Format the context strictly for the Judge
        context_string = "\n".join([getattr(res, 'payload', {}).get('text', '') for res in results])
        
        # 3. LLM-as-a-Judge Evaluation (Step 3 metrics)
        print(f"   -> Judging response quality...")
        llm_scores = evaluate_response_quality(query, context_string, answer)
        
        # Append structured data for JSON Export
        structured_evaluation_data.append({
            "query": query,
            "expected_source": expected,
            "expected_answer": expected_answer,
            "retrieval_hit": hit,
            "mrr": query_mrr,
            "latency": {"retrieval_ms": retrieval_time, "generation_ms": llm_time},
            "judge_scores": llm_scores,
            "generated_response": answer
        })
        
        # Build Markdown report logs
        report_lines.append(f"### Query {i}: {query}")
        report_lines.append(f"- **Expected Target Source:** `{expected}`")
        report_lines.append(f"- **Expected Answer Baseline:** {expected_answer}")
        report_lines.append(f"- **Retrieval Hit Accuracy:** {'✅ PASS' if hit else '❌ FAIL'} ({retrieval_time:.2f} ms)")
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
    avg_retrieval = calculate_average_metric(total_retrieval_time, len(test_subset))
    avg_llm = calculate_average_metric(total_llm_time, len(test_subset))
    final_hit_rate = calculate_hit_rate(hit_count, len(test_subset))
    final_mrr = calculate_average_metric(total_mrr, len(test_subset))
    
    # Prepend the high-level Executive Summary
    report_lines.insert(1, f"## Executive Summary Performance Metrics")
    report_lines.insert(2, f"- **Total System Queries Evaluated:** {len(test_subset)}")
    report_lines.insert(3, f"- **Retrieval Hit Rate (Accuracy):** {final_hit_rate:.2f}%")
    report_lines.insert(4, f"- **Mean Reciprocal Rank (MRR):** {final_mrr:.4f}")
    report_lines.insert(5, f"- **Average Retrieval Latency:** {avg_retrieval:.2f} ms")
    report_lines.insert(6, f"- **Average Generation Latency:** {avg_llm:.2f} ms\n")
    report_lines.insert(7, f"---")
    
    # Save Markdown File
    try:
        with open("evaluation_report.md", "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
    except Exception as e:
        logger.error(f"Failed to write markdown evaluation report: {e}", exc_info=True)

    # Save JSON File (Step 4 Fulfillment)
    try:
        with open("evaluation_results.json", "w", encoding="utf-8") as f:
            json.dump(structured_evaluation_data, f, indent=4)
        print("\n✅ Structured JSON evaluation data saved to 'evaluation_results.json'")
    except Exception as e:
        logger.error(f"Failed to save JSON results: {e}", exc_info=True)

    print("============ Evaluation Metrics Summary ============")
    print(f"🎯 Final Hit Rate: {final_hit_rate:.2f}%")
    print(f"📊 Mean Reciprocal Rank (MRR): {final_mrr:.4f}")
    print(f"⚡ Avg Retrieval Time: {avg_retrieval:.2f} ms")
    print(f"⚡ Avg Generation Time: {avg_llm:.2f} ms")
    print("====================================================")
    print(f"✅ Compliance check complete! Execution successfully evaluated {len(test_subset)} records.")

if __name__ == "__main__":
    run_enterprise_evaluation()