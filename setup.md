# 🚀 Enterprise RAG & Telemetry Architecture

Welcome to the environment initialization guide for the Enterprise AI Tools Knowledge Base. This repository features a fully monitored Retrieval-Augmented Generation (RAG) pipeline utilizing local Qdrant vector storage, OpenAI generation, and a detached Streamlit observability dashboard.

Follow this strict runbook to replicate the production environment on your local machine.

## ⚙️ Prerequisites

Ensure your host system meets the following core runtime requirements before proceeding:
- **Python:** Version 3.10 or higher
- **Git:** Latest stable release
- **Storage:** Minimum 500MB available for local vector index allocation

---

## Step 1: Clone the Repository

Clone the project architecture to your local environment using Git. Open your terminal and execute the following sequence:

```bash
git clone [https://github.com/waleedgohar167-Data/ai-tools-knowledge-base-rag.git](https://github.com/waleedgohar167-Data/ai-tools-knowledge-base-rag.git)
cd ai-tools-knowledge-base-rag
```

---

## Step 2: Initialize the Isolated Environment

To strictly prevent dependency collisions, you must isolate the runtime using a Python virtual environment.

**For Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**For macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```
*(You will know this is successful when `(venv)` appears at the start of your terminal prompt line.)*

---

## Step 3: Synchronize Dependencies

With the virtual environment active, install the pinned, production-grade dependencies to ensure absolute environment reproducibility:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 4: Configure Security Variables

This architecture requires external API keys for generation layers. A template has been provided to safely structure your local credentials.

1. Duplicate the template file:
   ```bash
   cp .env.example .env
   ```
2. Open the newly created `.env` file in your editor.
3. Inject your active OpenAI API key:
   ```env
   OPENAI_API_KEY=your_secure_openai_api_key_here
   ```
*(Note: The `.env` file is heavily restricted and ignored by Git to prevent credential leakage.)*

---

## Step 5: Initialize the Vector Database

Because the local vector database (`qdrant_local_data/`) and processed datasets are intentionally excluded from version control to maintain repository efficiency, you must build the index locally before querying the system.

Execute your ingestion pipeline to process the documents and generate the local Qdrant collections:

```bash
python ingest_data.py
```
*(Note: If your ingestion script is named differently, replace `ingest_data.py` with your exact filename.)*

---

## ✅ System Ready

Your environment is now completely initialized. Please refer to **`usage.md`** for the exact execution commands to launch both the interactive CLI pipeline and the Streamlit telemetry dashboard.