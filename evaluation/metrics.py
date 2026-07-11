# evaluation/metrics.py
from typing import List

def calculate_hit_rate(hit_count: int, total_queries: int) -> float:
    """
    Calculates the retrieval hit rate accuracy as a percentage.
    """
    if total_queries == 0:
        return 0.0
    return (hit_count / total_queries) * 100

def calculate_average_metric(total_value: float, total_queries: int) -> float:
    """
    Calculates the mathematical mean for latencies, processing times, or token consumption.
    """
    if total_queries == 0:
        return 0.0
    return total_value / total_queries

def calculate_mrr(retrieved_documents: List[str], expected_source: str) -> float:
    """
    Calculates the Reciprocal Rank (RR) for a single query evaluation.
    This is an elite RAG metric that scores *where* the correct document appeared.
    First place = 1.0, second place = 0.5, third place = 0.33, missing = 0.0.
    """
    for rank, doc_name in enumerate(retrieved_documents, start=1):
        if expected_source.lower() in doc_name.lower():
            return 1.0 / rank
    return 0.0