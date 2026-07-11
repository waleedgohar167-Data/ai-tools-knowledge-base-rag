import os
import json
import logging
import dlt
from datetime import datetime

# Configure enterprise logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = "data/sources"

@dlt.resource(name="ai_tools_documentation", write_disposition="replace")
def load_ai_tools_data():
    """
    dlt resource that extracts AI tools data from local JSON files,
    normalizes it, and appends retrieval metadata.
    """
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                tool_data = json.load(f)
                
                # Yield the structured and enriched record to dlt
                yield {
                    "tool": tool_data.get("tool_name"),
                    "content": tool_data.get("documentation", "") + " | Pricing: " + tool_data.get("pricing", ""),
                    "metadata_source_url": tool_data.get("source_url"),
                    "metadata_api_docs_url": tool_data.get("api_docs"),
                    "metadata_changelog_url": tool_data.get("changelog_url"), # Fully compliant requirement
                    "metadata_retrieval_timestamp": datetime.now().isoformat()
                }

if __name__ == "__main__":
    logger.info("Initializing dlt ingestion pipeline...")
    
# Configure the pipeline destination to duckdb in the processed folder
    pipeline = dlt.pipeline(
        pipeline_name="ai_knowledge_base",
        destination=dlt.destinations.duckdb("data/processed/ai_knowledge_base.duckdb"),
        dataset_name="staging_docs"
    )
    
    # Run the pipeline and load the data
    load_info = pipeline.run(load_ai_tools_data())
    
    logger.info("Pipeline run successfully! Load Summary:")
    print(load_info)