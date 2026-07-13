# Enterprise AI Tools Knowledge Base RAG

A production-grade Retrieval-Augmented Generation pipeline that ingests, embeds, and retrieves curated AI tool documentation through a semantic vector search engine. The system grounds every response in verified source material, eliminating hallucination by design. Built on Python 3.12, the architecture pairs a Qdrant vector database with OpenAI embeddings and generation, orchestrated through Docker Compose behind a custom bridge network. A `dlt`-powered ETL layer stages raw JSON through DuckDB before vectorization, while a Streamlit telemetry dashboard exposes real-time observability into retrieval accuracy, token consumption, and operational cost. The entire stack ships as a multi-stage Docker image running under a non-root user, achieving sub-two-second container boot times with zero host-level dependencies beyond Docker itself.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Dataset Description](#2-dataset-description)
3. [Architecture](#3-architecture)
4. [Installation](#4-installation)
5. [Configuration](#5-configuration)
6. [Usage](#6-usage)
7. [Evaluation Methodology](#7-evaluation-methodology)
8. [Monitoring & Observability](#8-monitoring--observability)
9. [Project Structure](#9-project-structure)
10. [Future Improvements](#10-future-improvements)

---

## 1. Problem Statement

The generative AI ecosystem spans hundreds of tools across orchestration frameworks, vector databases, code assistants, image generators, and multimodal platforms. Their documentation is fragmented across vendor sites, pricing pages shift without notice, and API specifications are scattered across changelogs, blog posts, and SDK references.

Engineers and technical decision-makers currently face three concrete problems:

- **Information fragmentation.** Comparing capabilities across tools (e.g., LangChain vs. LlamaIndex for RAG orchestration, or Pinecone vs. ChromaDB for vector storage) requires manually cross-referencing multiple documentation sites, often yielding outdated or incomplete answers.
- **LLM hallucination risk.** General-purpose language models will confidently fabricate pricing tiers, API parameters, and feature availability when asked about tools outside their training data. Without retrieval grounding, there is no mechanism to verify whether a generated answer reflects reality.
- **Decision latency.** Evaluating tool-specific details (token limits, rate limits, enterprise pricing, supported IDEs) takes hours of manual research per tool, compounding across multi-tool evaluations.

This RAG pipeline solves all three by maintaining a curated, version-controlled knowledge base of AI tool documentation, embedding it into a high-dimensional vector space, and constraining the LLM to generate responses exclusively from retrieved context. The system prompt enforces strict guardrails: if the retrieved documents do not contain the answer, the model responds with an explicit disclaimer rather than fabricating information.

---

## 2. Dataset Description

The knowledge base consists of **13 curated JSON documents**, each representing a major AI tool or platform. Every document follows a standardized schema:

| Field | Description |
|---|---|
| `tool_name` | Canonical name of the AI tool |
| `documentation` | Core feature and capability description |
| `pricing` | Subscription tiers and cost structure |
| `source_url` | Official documentation URL |
| `api_docs` | API reference endpoint |
| `changelog_url` | Release notes and version history link |
| `release_notes` | Summary of latest updates |

### Covered Tools

| Category | Tools |
|---|---|
| LLM Providers | Anthropic Claude, Google Gemini |
| Orchestration Frameworks | LangChain, LlamaIndex |
| Vector Databases | Pinecone, ChromaDB |
| Code Assistants | GitHub Copilot, Cursor |
| Productivity AI | Notion AI, Perplexity AI |
| Creative AI | Midjourney, CapCut |
| ML Platforms | Hugging Face |

### Ingestion Pipeline

The `dlt` (Data Load Tool) framework powers a two-stage ingestion architecture:

1. **Staging via `dlt` + DuckDB** (`ingestion/dlt_pipeline.py`): The `@dlt.resource` decorator defines a generator that iterates over `data/sources/*.json`, normalizes each record, appends ISO-formatted retrieval timestamps, and loads structured rows into a DuckDB staging table (`staging_docs`) for auditability and reprocessing.

2. **Vectorization via OpenAI + Qdrant** (`ingestion/ingest.py`): A direct-to-vector pipeline reads each JSON source, concatenates the documentation, pricing, API reference, and release notes into a single text chunk, generates a 1536-dimensional embedding via OpenAI's `text-embedding-ada-002` model, and upserts the resulting `PointStruct` into the `ai_tools_kb` Qdrant collection using cosine similarity.

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Docker Compose                               │
│                      (rag_network bridge)                           │
│                                                                     │
│  ┌──────────────────────────────┐  ┌─────────────────────────────┐  │
│  │   enterprise_ai_app (:8501)  │  │    qdrant_db (:6333)        │  │
│  │                              │  │                             │  │
│  │  ┌────────────────────────┐  │  │  ┌───────────────────────┐  │  │
│  │  │  Streamlit Dashboard   │  │  │  │  Qdrant Vector Store  │  │  │
│  │  │  (Telemetry & RAG UI)  │  │  │  │  Collection:          │  │  │
│  │  └────────┬───────────────┘  │  │  │   ai_tools_kb         │  │  │
│  │           │                  │  │  │  Vectors: 1536-dim     │  │  │
│  │  ┌────────▼───────────────┐  │  │  │  Distance: Cosine     │  │  │
│  │  │  Prompt Router         │  │  │  └───────────▲───────────┘  │  │
│  │  │  (Intent Detection)    │  │  │              │              │  │
│  │  │  general | comparison  │  │  │              │              │  │
│  │  │  summary | api         │  │  └──────────────┼──────────────┘  │
│  │  └────────┬───────────────┘  │                 │                 │
│  │           │                  │                 │                 │
│  │  ┌────────▼───────────────┐  │    Query Vector │                 │
│  │  │  Search Service        ├──┼────────────────►│                 │
│  │  │  (Embed + Retrieve)    │  │                 │                 │
│  │  └────────┬───────────────┘  │                 │                 │
│  │           │                  │                 │                 │
│  │  ┌────────▼───────────────┐  │                 │                 │
│  │  │  LLM Service           │  │                 │                 │
│  │  │  (gpt-3.5-turbo)       │  │                 │                 │
│  │  │  temp=0.3              │  │                 │                 │
│  │  └────────┬───────────────┘  │                 │                 │
│  │           │                  │                 │                 │
│  │  ┌────────▼───────────────┐  │                 │                 │
│  │  │  Analytics + Feedback  │  │                 │                 │
│  │  │  (JSON + CSV logging)  │  │                 │                 │
│  │  └────────────────────────┘  │                 │                 │
│  └──────────────────────────────┘                 │                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │  OpenAI API          │
                    │  • text-embedding-   │
                    │    ada-002           │
                    │  • gpt-3.5-turbo     │
                    └──────────────────────┘
```

**Data Flow:**

```
data/sources/*.json
       │
       ├──► dlt Pipeline ──► DuckDB (staging_docs)    [Audit & Replay]
       │
       └──► Ingest Pipeline ──► OpenAI Embeddings ──► Qdrant (ai_tools_kb)
                                                           │
User Query ──► Embed Query ──► Cosine Search ──────────────┘
                                    │
                              Top-K Results
                                    │
                              Prompt Router (Intent Detection)
                                    │
                              OpenAI gpt-3.5-turbo (temp=0.3)
                                    │
                              Grounded Response + Source Citations
                                    │
                              Analytics Service (JSON) + Feedback Service (CSV)
```

---

## 4. Installation

### Prerequisites

| Requirement | Version |
|---|---|
| Docker Engine | 20.10+ |
| Docker Compose | v2.0+ |
| Git | Latest stable |
| OpenAI API Key | Active billing account |

No local Python installation, virtual environment, or OS-specific toolchain is required. The multi-stage Dockerfile compiles all dependencies inside an isolated builder stage and copies only the production virtual environment into the final runner image based on `python:3.12-slim`.

### Clone and Launch

```bash
git clone https://github.com/waleedgohar167-Data/ai-tools-knowledge-base-rag.git
cd ai-tools-knowledge-base-rag
```

Create your environment file from the provided template:

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI API key (see [Configuration](#5-configuration)).

Build and launch the full stack:

```bash
docker-compose up -d --build
```

This command builds the multi-stage Docker image (builder + runner), starts the Qdrant vector database, waits for Qdrant readiness via `depends_on`, and launches the Streamlit dashboard. First build takes 2-3 minutes due to dependency compilation; subsequent starts complete in under two seconds.

### Local Development (Without Docker)

For contributors who need to modify and test code outside containers:

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
.\venv\Scripts\activate         # Windows PowerShell

pip install --upgrade pip
pip install -r requirements.txt
```

Ingest data into the local Qdrant instance:

```bash
python -m ingestion.ingest
```

---

## 5. Configuration

Duplicate `.env.example` to `.env` in the project root. This file is excluded from version control via `.gitignore` and from Docker build context via `.dockerignore`.

```env
# Required — OpenAI API key for embeddings and generation
OPENAI_API_KEY=your_secure_openai_api_key_here

# Optional — defaults shown
COLLECTION_NAME=ai_tools_kb
QDRANT_PATH=qdrant_local_data
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | Authenticates against the OpenAI API for both `text-embedding-ada-002` and `gpt-3.5-turbo` |
| `COLLECTION_NAME` | No | `ai_tools_kb` | Qdrant collection name for the vector index |
| `QDRANT_PATH` | No | `qdrant_local_data` | Local filesystem path for Qdrant persistent storage |

The application validates `OPENAI_API_KEY` at startup via `config/settings.py` and raises a hard `ValueError` if the key is missing, preventing silent failures.

---

## 6. Usage

### Start the Full Stack (Production)

```bash
docker-compose up -d --build
```

| Service | Container | Port | URL |
|---|---|---|---|
| Streamlit Dashboard | `enterprise_ai_app` | 8501 | `http://localhost:8501` |
| Qdrant Vector DB | `qdrant_db` | 6333 | `http://localhost:6333/dashboard` |

### Run the CLI Assistant

The interactive CLI provides a query-response loop with source citations and feedback collection:

```bash
python main.py
```

Example session:

```
Ask your question: What is the pricing for GitHub Copilot for businesses?

🔍 Searching vector database...
🧠 Generating grounded response...

==================================================
📝 AI RESPONSE
==================================================
The pricing for GitHub Copilot for businesses is $19 per user per month.

--------------------------------------------------
📚 SUPPORTING SOURCES
--------------------------------------------------
- GitHub Copilot (Confidence Score: 0.912)
==================================================

Was this answer helpful? (y/n): y
Optional comments (press Enter to skip):
✅ Thank you! Your feedback has been securely recorded.
```

### Run the dlt Staging Pipeline

Load source documents into the DuckDB staging table for audit and reprocessing:

```bash
python -m ingestion.dlt_pipeline
```

### Run the Evaluation Framework

Execute the full 50-query benchmark suite:

```bash
python -m evaluation.run_evaluation
```

This generates `evaluation_report.md` with per-query accuracy, reciprocal rank scores, latency profiles, and an executive summary.

### Run the Top-K Optimization Sweep

Benchmark retrieval performance across different `limit` values (3, 5, 10):

```bash
python -m evaluation.optimize_retrieval
```

### Tear Down

```bash
docker-compose down
```

Persistent data in `qdrant_local_data/` and `logs/` is retained across restarts via Docker volume mounts.

---

## 7. Evaluation Methodology

The evaluation framework (`evaluation/run_evaluation.py`) executes a **50-query benchmark suite** spanning all 13 indexed tools. Each query is paired with an `expected_source` label, enabling automated accuracy verification.

### Metrics

| Metric | Definition | Implementation |
|---|---|---|
| **Retrieval Hit Rate** | Percentage of queries where the expected tool appears anywhere in the Top-5 results | `evaluation/metrics.py:calculate_hit_rate` |
| **Mean Reciprocal Rank (MRR)** | Average of `1/rank` for the position of the expected tool in results (1st = 1.0, 2nd = 0.5, 3rd = 0.33, absent = 0.0) | `evaluation/metrics.py:calculate_mrr` |
| **Average Retrieval Latency** | Mean wall-clock time for embedding generation + Qdrant cosine search | Measured via `time.perf_counter()` in `search_service.py` |
| **Average Generation Latency** | Mean wall-clock time for OpenAI `gpt-3.5-turbo` completion | Measured via `time.perf_counter()` in `llm_service.py` |

### Results

The most recent evaluation run produced the following results:

| Metric | Value |
|---|---|
| Total Benchmark Queries | 50 |
| Retrieval Hit Rate | 100.00% |
| Mean Reciprocal Rank | 1.0000 |
| Average Retrieval Latency | 412.79 ms |
| Average Generation Latency | 1864.36 ms |

A perfect MRR of 1.0 indicates that the expected tool document was ranked first in every single query across the benchmark. The full per-query breakdown with response previews, token consumption, and source citations is available in `evaluation_report.md`.

### Top-K Optimization

The retrieval optimization sweep (`evaluation/optimize_retrieval.py`) benchmarks three `limit` configurations (3, 5, 10) across a 5-query sample, measuring average processing time against average cosine similarity score. The recommended production configuration is the limit that achieves >0.70 similarity with <50ms per-query processing time.

---

## 8. Monitoring & Observability

### Streamlit Telemetry Dashboard

The dashboard (`dashboard.py`) renders real-time operational metrics in a Vercel-inspired minimal UI accessible at `http://localhost:8501`:

**Core Pipeline Metrics:**
- Total Invocations (cumulative request count)
- Retrieval Success Rate (percentage)
- P99 Response Latency (milliseconds)
- Operational Cost (estimated USD based on $0.002/1K tokens)

**Resource Utilization Gauges:**
- API Reliability Target (Plotly gauge, emerald green)
- Context Window Token Volume (Plotly gauge, cumulative token counter)

**Vector Space Infrastructure:**
- Indexed Documents count
- Active Embeddings count
- Successful vs. Failed query operations

**User Interaction Ledger:**
- High-frequency query analysis (top 5 by volume)
- Raw feedback stream with color-coded ratings (green for Helpful, red for Not Helpful)

### Logging Architecture

The logging system (`app_logging/logger.py`) implements a dual-output handler:

| Handler | Target | Rotation | Retention |
|---|---|---|---|
| `StreamHandler` | `stdout` (container logs) | — | — |
| `TimedRotatingFileHandler` | `logs/enterprise_rag.log` | Midnight daily | 30 days |

Log format: `%(asctime)s - %(levelname)s - [%(name)s] - %(message)s`

Each service module registers its own named logger (`Main_Application`, `Search_Service`, `LLM_Service`, `Analytics_Service`, `Feedback_Service`, `Qdrant_Ingestion`, `OpenAI_Client_Service`, `Evaluation_Framework`), enabling per-component filtering.

### Persistent Volume Mounts

| Host Path | Container Path | Contents |
|---|---|---|
| `./logs` | `/app/logs` | `enterprise_rag.log`, `application_analytics.json`, `user_feedback.csv` |
| `./qdrant_local_data` | `/qdrant/storage` | Qdrant WAL, segments, and index files |

### Analytics Service

The analytics engine (`services/analytics_service.py`) records every transaction to `logs/application_analytics.json`, tracking:

- Cumulative request counts (total, successful, failed)
- Running average retrieval and generation latencies
- Total token consumption
- Estimated API cost (calculated at $0.002 per 1,000 tokens)

### Feedback Service

User feedback is appended to `logs/user_feedback.csv` with columns: `Timestamp`, `Rating`, `Comments`, `Original Question`, `Generated Answer`. The dashboard parses this file to surface high-frequency queries and color-coded satisfaction ratings.

---

## 9. Project Structure

```
ai-tools-knowledge-base-rag/
├── dashboard.py                    # Streamlit telemetry and observability UI
├── main.py                         # Interactive CLI application loop
├── docker-compose.yml              # Two-service orchestration (app + qdrant)
├── Dockerfile                      # Multi-stage build (builder → runner)
├── requirements.txt                # Pinned production dependencies
├── .env.example                    # Environment variable template
├── .dockerignore                   # Build context exclusions
├── .gitignore                      # Version control exclusions
│
├── config/
│   └── settings.py                 # Centralized environment configuration
│
├── ingestion/
│   ├── dlt_pipeline.py             # dlt + DuckDB staging pipeline
│   └── ingest.py                   # Direct-to-Qdrant vector ingestion
│
├── services/
│   ├── search_service.py           # Embedding + Qdrant cosine search
│   ├── llm_service.py              # OpenAI gpt-3.5-turbo generation
│   ├── analytics_service.py        # JSON-based transaction analytics
│   ├── feedback_service.py         # CSV-based user feedback logging
│   └── openai_client.py            # OpenAI client wrapper with diagnostics
│
├── prompts/
│   └── templates.py                # Intent-routed prompt templates
│
├── evaluation/
│   ├── metrics.py                  # Hit rate, MRR, average metric functions
│   ├── run_evaluation.py           # 50-query benchmark framework
│   └── optimize_retrieval.py       # Top-K retrieval optimization sweep
│
├── utils/
│   ├── chunk_documents.py          # Word-based text chunking (500/100 overlap)
│   └── generate_embeddings.py      # Batch embedding generation utility
│
├── app_logging/
│   └── logger.py                   # Dual-output rotating file logger
│
├── data/
│   ├── sources/                    # 13 curated AI tool JSON documents
│   └── processed/                  # DuckDB staging DB + processed chunks
│
├── logs/                           # Runtime logs, analytics, feedback
│   ├── enterprise_rag.log
│   ├── application_analytics.json
│   └── user_feedback.csv
│
└── evaluation_report.md            # Generated 50-query benchmark report
```

---

## 10. Future Improvements

**1. Chunking Strategy and Hybrid Retrieval.** The current pipeline embeds each tool as a single monolithic document. Implementing hierarchical chunking with configurable window sizes (e.g., 512-token chunks with 64-token overlap) paired with a hybrid retrieval strategy combining dense vector search with BM25 sparse retrieval would significantly improve precision on granular queries such as specific API parameters or nested pricing tiers. This also enables re-ranking via a cross-encoder model to surface the most contextually relevant passages before generation.

**2. Automated Ingestion via Scheduled Pipelines.** The knowledge base currently relies on manually curated JSON files. Integrating scheduled web scrapers or API connectors into the `dlt` pipeline — triggered by an orchestration framework such as Prefect or Airflow — would enable automated documentation drift detection, ensuring the vector index reflects the latest vendor documentation without manual intervention.

**3. Multi-Tenant Deployment with Authentication.** The current architecture serves a single unauthenticated Streamlit instance. For production-scale deployment, the system should be fronted by an API gateway (e.g., NGINX or Traefik) with OAuth 2.0 / OIDC authentication, namespace-isolated Qdrant collections per tenant, and horizontal scaling of the application container behind a load balancer with health-check probes on the `/healthz` endpoint.

---

## License

This project is developed for educational and portfolio purposes.
