import json
import os

eval_file = "evaluation/results.json"
analytics_file = "logs/application_analytics.json"

if not os.path.exists(eval_file):
    print(f"❌ Error: Could not find '{eval_file}'. Please ensure your evaluation script ran successfully.")
    exit(1)

# Load the benchmark results
with open(eval_file, "r", encoding="utf-8") as f:
    eval_data = json.load(f)

analytics_data = []
# Load existing analytics safely
if os.path.exists(analytics_file):
    with open(analytics_file, "r", encoding="utf-8") as f:
        try:
            loaded_data = json.load(f)
            if isinstance(loaded_data, list):
                analytics_data = loaded_data
            elif isinstance(loaded_data, dict):
                analytics_data = loaded_data.get("details", [loaded_data])
        except json.JSONDecodeError:
            pass

# Safely extract benchmark details
details = eval_data.get("details", [])

for item in details:
    # Safely handle both nested ('latency': {'retrieval_ms': ...}) and flat formats
    latency_info = item.get("latency", {}) if isinstance(item.get("latency"), dict) else {}
    retrieval_ms = latency_info.get("retrieval_ms", item.get("retrieval_time_ms", 0.0))
    generation_ms = latency_info.get("generation_ms", item.get("generation_time_ms", 0.0))
    tokens = item.get("tokens_used", 0)

    analytics_data.append({
        "query": item.get("query", ""),
        "retrieval_latency_ms": retrieval_ms,
        "generation_latency_ms": generation_ms,
        "tokens_used": tokens,
        "source": "50-query-benchmark"
    })

# Ensure the logs directory exists
os.makedirs(os.path.dirname(analytics_file), exist_ok=True)

# Save it back to application_analytics.json
with open(analytics_file, "w", encoding="utf-8") as f:
    json.dump(analytics_data, f, indent=4)

print("✅ application_analytics.json successfully updated with 50-query metrics!")