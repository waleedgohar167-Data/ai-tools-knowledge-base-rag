# ⚙️ Application Operations & Execution Runbook

This operational guide details the execution commands required to run the independent subsystems of the Enterprise RAG Architecture. Ensure your virtual environment is active and your `.env` credentials are set before initiating any subsystem.

## Subsystem 1: Core Knowledge Base Engine (CLI)
The primary interactive Retrieval-Augmented Generation (RAG) pipeline. This interface handles user queries, semantic vector search, LLM generation, and real-time telemetry logging.

**Execution Command:**
```bash
python main.py
```

**Operational Flow:**
1. The system will initialize the Qdrant vector client and OpenAI embedding engine.
2. Input your query at the secure prompt (e.g., *"What is the enterprise pricing for LangChain?"*).
3. Review the AI-generated response and the verifiable source citations.
4. Provide qualitative feedback (`y/n`) and optional comments to securely log the transaction into the local CSV database.
5. Type `exit` to trigger a graceful system teardown.

---

## Subsystem 2: Observability & Telemetry Dashboard (UI)
A detached, enterprise-grade Streamlit web console providing real-time visibility into system latency, token consumption, financial API costs, and user feedback metrics.

**Execution Command:**
```bash
streamlit run dashboard.py
```

**Operational Flow:**
1. Execute the command in a new terminal instance (ensure the `venv` is active).
2. The application will bind to a local port and launch automatically in your default browser at `http://localhost:8501`.
3. The dashboard actively parses `logs/application_analytics.json` and `logs/user_feedback.csv` to render live metric updates in a highly structured FinTech-style UI.

---

## Subsystem 3: Automated Evaluation Framework (CI/CD)
The rigorous 50-question compliance benchmark suite designed to calculate Retrieval Hit Rate (Accuracy), Mean Reciprocal Rank (MRR), and system latency profiles.

**Execution Command:**
```bash
python -m evaluation.run_evaluation
```

**Operational Flow:**
1. The framework will dynamically iterate through the 50 golden benchmark queries.
2. Upon completion, it will compile and generate a comprehensive markdown artifact (`evaluation_report.md`).
3. A high-level executive summary of the system's total accuracy, rank distributions, and latency averages will be output directly to the terminal for rapid review.