# evaluation/run_evaluation.py
import time
from services.search_service import search
from services.llm_service import generate_response
from evaluation.metrics import calculate_hit_rate, calculate_average_metric, calculate_mrr
from app_logging.logger import get_logger

# Initialize our centralized application logging
logger = get_logger("Evaluation_Framework")

# Comprehensive, rigorous 50-question enterprise evaluation dataset
DATASET = [
    # --- LangChain ---
    {"query": "What is the enterprise pricing for LangChain?", "expected_source": "LangChain"},
    {"query": "How does LangChain handle vector store abstractions?", "expected_source": "LangChain"},
    {"query": "Give me an example of a LangChain expression language LCEL chain.", "expected_source": "LangChain"},
    {"query": "What are the latest production release notes for LangChain?", "expected_source": "LangChain"},
    
    # --- Cursor ---
    {"query": "Explain how Cursor integrates with VS Code.", "expected_source": "Cursor"},
    {"query": "What are the indexing capabilities of Cursor for large codebases?", "expected_source": "Cursor"},
    {"query": "Does Cursor support multi-line editing using AI commands?", "expected_source": "Cursor"},
    {"query": "What is the pricing model for Cursor Pro and Business tiers?", "expected_source": "Cursor"},
    
    # --- Pinecone ---
    {"query": "Compare Pinecone and ChromaDB pricing.", "expected_source": "Pinecone"},
    {"query": "What is the architecture behind Pinecone serverless indexes?", "expected_source": "Pinecone"},
    {"query": "How does Pinecone handle multi-tenant vector isolation?", "expected_source": "Pinecone"},
    {"query": "What is the maximum vector dimension supported by Pinecone?", "expected_source": "Pinecone"},
    
    # --- Anthropic Claude ---
    {"query": "What is the token limit for Anthropic Claude 3.5 Sonnet?", "expected_source": "Anthropic Claude"},
    {"query": "How do Anthropic Claude artifacts work in a development workflow?", "expected_source": "Anthropic Claude"},
    {"query": "What are the specific fine-tuning parameters for Claude models?", "expected_source": "Anthropic Claude"},
    {"query": "Compare the cost per million tokens for Claude 3.5 Sonnet vs Opus.", "expected_source": "Anthropic Claude"},
    
    # --- LlamaIndex ---
    {"query": "Summarize what LlamaIndex does for RAG pipelines.", "expected_source": "LlamaIndex"},
    {"query": "How do you build a hierarchical node parser in LlamaIndex?", "expected_source": "LlamaIndex"},
    {"query": "What vector database integrations are supported natively by LlamaIndex?", "expected_source": "LlamaIndex"},
    {"query": "Explain property graph indexes in LlamaIndex framework.", "expected_source": "LlamaIndex"},
    
    # --- GitHub Copilot ---
    {"query": "What is the pricing for GitHub Copilot for businesses?", "expected_source": "GitHub Copilot"},
    {"query": "How does GitHub Copilot Enterprise handle private repository indexing?", "expected_source": "GitHub Copilot"},
    {"query": "What IDEs are natively supported by the GitHub Copilot extension?", "expected_source": "GitHub Copilot"},
    {"query": "Does GitHub Copilot offer fine-grained telemetry control for security?", "expected_source": "GitHub Copilot"},
    
    # --- Notion AI ---
    {"query": "Show me the release notes for Notion AI.", "expected_source": "Notion AI"},
    {"query": "What are the block-level automation features of Notion AI?", "expected_source": "Notion AI"},
    {"query": "How does Notion AI preserve workspace permissions when querying?", "expected_source": "Notion AI"},
    {"query": "What is the monthly add-on pricing for Notion AI for teams?", "expected_source": "Notion AI"},
    
    # --- Perplexity AI ---
    {"query": "What models are available on Perplexity Pro?", "expected_source": "Perplexity AI"},
    {"query": "Explain the multi-source citation mechanism of Perplexity Pro.", "expected_source": "Perplexity AI"},
    {"query": "What is the API key rate limit for Perplexity Sonar models?", "expected_source": "Perplexity AI"},
    {"query": "How does Perplexity handle file uploads and data parsing?", "expected_source": "Perplexity AI"},
    
    # --- CapCut ---
    {"query": "What are the enterprise cloud storage limits for CapCut Pro teams?", "expected_source": "CapCut"},
    {"query": "How do you leverage CapCut's AI script-to-video generation features?", "expected_source": "CapCut"},
    {"query": "Does CapCut provide programmatic API access for batch rendering?", "expected_source": "CapCut"},
    {"query": "What are the monthly subscription costs for CapCut Business?", "expected_source": "CapCut"},
    
    # --- ChromaDB ---
    {"query": "Is ChromaDB capable of running completely in-memory for testing?", "expected_source": "ChromaDB"},
    {"query": "How do you configure metadata filtering expressions in ChromaDB?", "expected_source": "ChromaDB"},
    {"query": "What embedding functions are built-in natively to ChromaDB?", "expected_source": "ChromaDB"},
    {"query": "Explain the cluster deployment model for enterprise ChromaDB.", "expected_source": "ChromaDB"},
    
    # --- Google Gemini ---
    {"query": "What is the context window size for Google Gemini 1.5 Pro?", "expected_source": "Google Gemini"},
    {"query": "How does Gemini 1.5 Flash handle native multimodal video inputs?", "expected_source": "Google Gemini"},
    {"query": "What are the pricing tiers for Google AI Studio API access?", "expected_source": "Google Gemini"},
    {"query": "Explain how Gemini cache tokens optimize repeating context costs.", "expected_source": "Google Gemini"},
    
    # --- Hugging Face ---
    {"query": "What is the difference between Hugging Face Spaces and Inference Endpoints?", "expected_source": "Hugging Face"},
    {"query": "How does Hugging Face manage security for gated model architectures?", "expected_source": "Hugging Face"},
    {"query": "What is the enterprise pricing model for Hugging Face PRO accounts?", "expected_source": "Hugging Face"},
    {"query": "Explain how the Hugging Face Hub handles optimized git LFS tracking.", "expected_source": "Hugging Face"},
    
    # --- Midjourney ---
    {"query": "What are the pricing parameters for Midjourney Mega plan subscription?", "expected_source": "Midjourney"},
    {"query": "How do you utilize the Midjourney API for commercial applications?", "expected_source": "Midjourney"}
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
    
    for i, item in enumerate(DATASET, 1):
        query = item["query"]
        expected = item["expected_source"]
        print(f"🔄 Testing [{i}/{len(DATASET)}]: \"{query}\"")
        
        # 1. Evaluate Semantic Retrieval Performance (Perfect Tuple Unpacking)
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
        
        # 2. Evaluate LLM Generation Performance (Perfect Tuple Unpacking)
        answer, llm_time, tokens = generate_response(query, results)
        total_llm_time += llm_time
        
        # Build individual logs
        report_lines.append(f"### Query {i}: {query}")
        report_lines.append(f"- **Expected Target Source:** `{expected}`")
        report_lines.append(f"- **Retrieval Hit Accuracy:** {'✅ PASS' if hit else '❌ FAIL'} ({retrieval_time:.2f} ms)")
        report_lines.append(f"- **Reciprocal Rank (RR):** `{query_mrr:.4f}`")
        report_lines.append(f"- **Source Citations (Top-K):** {', '.join(citations) if citations else 'None'}")
        report_lines.append(f"- **LLM Generation Latency:** {llm_time:.2f} ms")
        report_lines.append(f"- **Approximate Token Consumption:** ~{tokens} tokens")
        report_lines.append(f"- **Generated Response Preview:**\n> {answer[:200].replace('\n', ' ')}...\n")

    # 3. Compute Aggregated Global Metrics
    avg_retrieval = calculate_average_metric(total_retrieval_time, len(DATASET))
    avg_llm = calculate_average_metric(total_llm_time, len(DATASET))
    final_hit_rate = calculate_hit_rate(hit_count, len(DATASET))
    final_mrr = calculate_average_metric(total_mrr, len(DATASET))
    
    # Prepend the high-level Executive Summary
    report_lines.insert(1, f"## Executive Summary Performance Metrics")
    report_lines.insert(2, f"- **Total System Queries Evaluated:** {len(DATASET)}")
    report_lines.insert(3, f"- **Retrieval Hit Rate (Accuracy):** {final_hit_rate:.2f}%")
    report_lines.insert(4, f"- **Mean Reciprocal Rank (MRR):** {final_mrr:.4f}")
    report_lines.insert(5, f"- **Average Retrieval Latency:** {avg_retrieval:.2f} ms")
    report_lines.insert(6, f"- **Average Generation Latency:** {avg_llm:.2f} ms\n")
    report_lines.insert(7, f"---")
    
    try:
        with open("evaluation_report.md", "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
            
        print("\n============ Evaluation Metrics Summary ============")
        print(f"🎯 Final Hit Rate: {final_hit_rate:.2f}%")
        print(f"📊 Mean Reciprocal Rank (MRR): {final_mrr:.4f}")
        print(f"⚡ Avg Retrieval Time: {avg_retrieval:.2f} ms")
        print(f"⚡ Avg Generation Time: {avg_llm:.2f} ms")
        print("====================================================")
        print(f"✅ Compliance check complete! 'evaluation_report.md' generated with {len(DATASET)} records.")
    except Exception as e:
        logger.error(f"Failed to write evaluation report artifact: {e}", exc_info=True)

if __name__ == "__main__":
    run_enterprise_evaluation()