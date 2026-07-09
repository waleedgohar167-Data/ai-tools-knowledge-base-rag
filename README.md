# AI Tools Knowledge Base Assistant

## Problem Statement
The landscape of generative AI tools (video, image, text, and orchestration) is expanding rapidly. Navigating fragmented documentation, pricing models, and API limitations across different platforms takes significant time. This project builds a unified AI Assistant capable of instantly retrieving accurate, up-to-date information regarding various AI tools, allowing developers and creators to optimize their workflows efficiently.

## Target Users
* Data Scientists and AI Engineers looking for the best deployment or orchestration tools.
* Digital Content Creators requiring rapid comparisons between video and image generation platforms.
* Developers needing quick API capabilities and limits.

## Proposed Dataset
The dataset will be built using the `dlt` (data load tool) library to ingest:
* Official documentation from major AI tools (e.g., Midjourney, Gemini, CapCut, Kestra).
* Tool pricing structures and API rate limits.
* Capability matrices and feature updates.

## Core Features
* **Retrieval-Augmented Generation (RAG):** Context-aware querying utilizing a vector database for precise tool comparisons.
* **Automated Data Ingestion:** Automated pipelines pulling the latest documentation updates.
* **Evaluation & Monitoring:** End-to-end pipeline evaluation focusing on answer quality and retrieval metrics.
* **Orchestration:** Workflow management integrated to keep the knowledge base current.


9 july status,

1. Enterprise-Grade Architecture & Security Setup
Environment Instantiation: Established an isolated Python virtual environment, locking down core dependencies (dlt[duckdb], openai, python-dotenv) in a version-controlled requirements.txt.
Modular Codebase Design: Architected the complete directory structure (app/, ingestion/, indexing/, rag/, evaluation/, orchestration/, data/sources/, docs/, tests/) strictly adhering to the Capstone Planning Document to ensure seamless scalability.
Security Protocol: Implemented strict .env variable management to ensure the OpenAI API key and future credentials are fully secured and ignored by Git.

2. State-of-the-Art LLM Integration (RAG Core Foundation)
Object-Oriented Client Architecture: Developed a reusable OpenAIIntegration class (app/openai_client.py) equipped with enterprise-grade logging and precise exception handling (Network, Authentication, and Rate Limit errors).
Model Optimization & Debugging: Proactively upgraded the generation model from the legacy gpt-3.5-turbo to the cutting-edge gpt-5.4-mini to maximize reasoning capabilities within our $5 budget.
Parameter Resolution: Successfully debugged and resolved an HTTP 400 parameter shift inherent to newer reasoning models (mapping max_tokens to max_completion_tokens), achieving a flawless 200 OK connection verification.

3. Data Engineering & Automated Ingestion Pipeline
Compliant Dataset Construction: Hand-curated the initial Phase 1 knowledge base for Google Gemini, Midjourney, and CapCut. I ensured strict compliance with all data requirements by proactively auditing the schema to include documentation, pricing, API references, and changelog URLs.
dlt Pipeline Implementation: Engineered a highly reusable data load tool (dlt) pipeline (ingestion/dlt_pipeline.py) utilizing DuckDB as the staging destination.
Metadata Enrichment: Programmed the ingestion engine to parse the raw JSON files, normalize the content, and dynamically append ISO-formatted retrieval timestamps and source URLs to guarantee source attribution during the final RAG generation phase.
Execution Results: The pipeline executed perfectly with zero failed jobs, loading the structured records into the staging_docs DuckDB table in under a second.


## Development Roadmap
* **Week 1:** Finalize dataset ingestion pipeline using `dlt` and establish the vector database.
* **Week 2:** Implement the core RAG architecture and evaluate offline/online metrics.
* **Week 3:** Integrate orchestration workflows and finalize answer quality monitoring.
* **Week 4:** Final deployment, testing, and submission.
