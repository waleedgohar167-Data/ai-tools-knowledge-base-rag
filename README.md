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

## Development Roadmap
* **Week 1:** Finalize dataset ingestion pipeline using `dlt` and establish the vector database.
* **Week 2:** Implement the core RAG architecture and evaluate offline/online metrics.
* **Week 3:** Integrate orchestration workflows and finalize answer quality monitoring.
* **Week 4:** Final deployment, testing, and submission.
