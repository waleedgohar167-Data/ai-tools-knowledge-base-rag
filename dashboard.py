# dashboard.py
import streamlit as st
import pandas as pd
import json
import os
from typing import Any

import plotly.graph_objects as go

# IMPROVEMENT: Centralized Configuration Imports
from config.settings import ANALYTICS_FILE, FEEDBACK_FILE, RETRIEVAL_LIMIT

from services.search_service import search
from services.llm_service import generate_response
from services.analytics_service import record_transaction
from services.feedback_service import save_feedback

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Tools Knowledge Base",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Minimal, enterprise-grade CSS
# ---------------------------------------------------------------------------
st.markdown("""

""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data Loading Helpers
# ---------------------------------------------------------------------------

def load_analytics() -> dict:
    """Load the cumulative analytics JSON or return sensible defaults."""
    if os.path.exists(ANALYTICS_FILE):
        try:
            with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        # IMPROVEMENT: Explicit error logging for analytics masking
        except json.JSONDecodeError as e:
            print(f"WARNING: Analytics file is corrupted. Reverting to defaults. Error: {e}")
        except IOError as e:
            print(f"WARNING: Could not read analytics file. Error: {e}")
            
    return {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "average_response_time_ms": 0,
        "estimated_api_cost_usd": 0,
        "total_tokens_consumed": 0,
    }


def load_feedback() -> pd.DataFrame | None:
    """Load user feedback CSV if it exists."""
    if os.path.exists(FEEDBACK_FILE):
        try:
            return pd.read_csv(FEEDBACK_FILE)
        except Exception:
            return None
    return None


# ---------------------------------------------------------------------------
# UI Components
# ---------------------------------------------------------------------------

def render_sidebar() -> None:
    """Render the sidebar with project context, instructions, and live system status."""
    with st.sidebar:
        st.title("AI Tools Knowledge Base")
        st.caption("Retrieval-Augmented Generation Pipeline")

        st.markdown("---")
        st.markdown("**How to use**")
        st.markdown(
            "Ask any question about the 13 indexed AI tools. "
            "The system retrieves relevant documentation from the vector database "
            "and generates a grounded answer with source citations."
        )

        st.markdown("---")
        st.markdown("**Indexed Tools**")
        tools = [
            "Anthropic Claude", "Google Gemini", "LangChain", "LlamaIndex",
            "Pinecone", "ChromaDB", "GitHub Copilot", "Cursor",
            "Notion AI", "Perplexity AI", "Midjourney", "CapCut", "Hugging Face",
        ]
        st.markdown("  \n".join(f"• {t}" for t in tools))

        st.markdown("---")
        st.markdown("**System Status**")
        data = load_analytics()
        total = data.get("total_requests", 0)
        success = data.get("successful_requests", 0)
        rate = (success / max(total, 1)) * 100
        st.metric("Queries Processed", f"{total:,}")
        st.metric("Success Rate", f"{rate:.0f}%")
        st.metric("Est. API Cost", f"${data.get('estimated_api_cost_usd', 0):.4f}")

        st.markdown("---")
        st.caption("Built with Streamlit · Qdrant · OpenAI")


def render_telemetry_tab() -> None:
    """Render the full telemetry and observability dashboard."""
    data = load_analytics()
    total_reqs = max(data.get("total_requests", 1), 1)
    success_rate = (data.get("successful_requests", 0) / total_reqs) * 100

    st.header("Core Pipeline Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Invocations", f"{data.get('total_requests', 0):,}")
    col2.metric("Retrieval Success Rate", f"{success_rate:.1f}%")
    col3.metric("Avg Response Latency", f"{data.get('average_response_time_ms', 0):.1f} ms")
    col4.metric("Operational Cost (USD)", f"${data.get('estimated_api_cost_usd', 0):.4f}")

    st.header("Resource Utilization")
    col_g1, col_g2 = st.columns(2)

    def _gauge(value: float, title: str, max_val: float, color: str) -> go.Figure:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": title, "font": {"size": 14, "color": "#6b7280", "family": "Inter"}},
            gauge={
                "axis": {"range": [None, max_val], "visible": False},
                "bar": {"color": color, "thickness": 0.3},
                "bgcolor": "#f3f4f6",
                "borderwidth": 0,
            },
            number={"font": {"color": "#111827", "size": 36, "family": "Inter"}},
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=250,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        return fig

    with col_g1:
        st.plotly_chart(_gauge(success_rate, "API Reliability (%)", 100, "#10b981"), use_container_width=True)
    with col_g2:
        st.plotly_chart(
            _gauge(data.get("total_tokens_consumed", 0), "Token Volume", 50000, "#374151"),
            use_container_width=True,
        )

    st.header("Vector Space Infrastructure")
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Indexed Documents", "13")
    c6.metric("Active Embeddings", "13")
    c7.metric("Successful Queries", f"{data.get('successful_requests', 0):,}")
    c8.metric("Failed Operations", f"{data.get('failed_requests', 0):,}")

    st.header("User Interaction Ledger")
    df = load_feedback()
    if df is not None and not df.empty:
        col_faq, col_stream = st.columns([1, 2])
        with col_faq:
            st.markdown("**High-Frequency Queries**")
            faq = df["Original Question"].value_counts().reset_index()
            faq.columns = ["Query", "Volume"]
            st.dataframe(faq.head(5), use_container_width=True, hide_index=True)
        with col_stream:
            st.markdown("**Feedback Stream**")
            styled = df.style.map(
                lambda x: "color: #10b981; font-weight: 600;" if x == "Helpful"
                else ("color: #ef4444; font-weight: 600;" if x == "Not Helpful" else ""),
                subset=["Rating"],
            )
            st.dataframe(styled, use_container_width=True)
    else:
        st.info("No user feedback recorded yet. Start asking questions in the Chat tab.")


def render_source_citations(results: list[Any], retrieval_ms: float) -> None:
    """Render retrieved source documents as expandable citation blocks."""
    st.markdown(f"*Retrieved {len(results)} sources in {retrieval_ms:.0f} ms*")
    for i, res in enumerate(results, 1):
        if isinstance(res, dict):
            payload = res.get("payload", {}) or {}
            score = res.get("score", 0.0)
        else:
            payload = getattr(res, "payload", {}) or {}
            score = getattr(res, "score", 0.0)

        tool_name = payload.get("tool", payload.get("document_name", "Unknown"))
        source_url = payload.get("source_url", "")
        chunk_text = payload.get("chunk_text", "No content available.")

        with st.expander(f"Source {i}: **{tool_name}** — Relevance: {score:.3f}", expanded=False):
            st.markdown(f"**Tool:** {tool_name}")
            if source_url:
                st.markdown(f"**URL:** {source_url}")
            st.markdown(f"**Cosine Similarity:** `{score:.4f}`")
            st.markdown("---")
            st.text(chunk_text[:1500])


def render_chat_tab() -> None:
    """Render the RAG chat interface with source citations and feedback."""
    st.markdown("Ask a question about any of the 13 indexed AI tools. "
                "Responses are grounded exclusively in retrieved documentation.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "sources" in msg:
                render_source_citations(msg["sources"], msg.get("retrieval_ms", 0))
                _render_feedback_buttons(idx, msg)

    if prompt := st.chat_input("e.g. What is the pricing for GitHub Copilot?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching vector database..."):
                # IMPROVEMENT: Use the centralized limit from config
                search_res = search(prompt, limit=RETRIEVAL_LIMIT)
                results = search_res[0] if isinstance(search_res, tuple) else search_res
                retrieval_ms = search_res[1] if isinstance(search_res, tuple) and len(search_res) > 1 else 0.0

            if not results:
                no_results_msg = "No relevant documents found. Please try rephrasing your question."
                st.warning(no_results_msg)
                st.session_state.messages.append({"role": "assistant", "content": no_results_msg, "sources": []})
                record_transaction(success=False, retrieval_time=retrieval_ms)
            else:
                with st.spinner("Generating grounded response..."):
                    gen_res = generate_response(prompt, results)
                    answer = gen_res[0] if isinstance(gen_res, tuple) else gen_res
                    gen_ms = gen_res[1] if isinstance(gen_res, tuple) and len(gen_res) > 1 else 0.0
                    tokens = gen_res[2] if isinstance(gen_res, tuple) and len(gen_res) > 2 else 0

            st.markdown(answer)
            render_source_citations(results, retrieval_ms)

            record_transaction(
                success=True,
                retrieval_time=retrieval_ms,
                generation_time=gen_ms,
                tokens=tokens,
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": results,
                "retrieval_ms": retrieval_ms,
                "gen_ms": gen_ms,
                "tokens": tokens,
                "query": prompt,
            })
            
            # Explicitly render the buttons for the brand new message instantly!
            _render_feedback_buttons(len(st.session_state.messages) - 1, st.session_state.messages[-1])


def _render_feedback_buttons(idx: int, msg: dict) -> None:
    """Render thumbs-up / thumbs-down feedback buttons for a response."""
    feedback_key = f"feedback_{idx}"
    if feedback_key in st.session_state:
        rating = st.session_state[feedback_key]
        st.caption(f"{'👍' if rating else '👎'} Feedback recorded — thank you!")
        return

    col_up, col_down, _ = st.columns([1, 1, 8])
    with col_up:
        if st.button("👍", key=f"up_{idx}", help="Helpful"):
            st.session_state[feedback_key] = True
            save_feedback(
                msg.get("query", ""),
                msg["content"],
                True,
                "",
            )
            st.rerun()
    with col_down:
        if st.button("👎", key=f"down_{idx}", help="Not helpful"):
            st.session_state[feedback_key] = False
            save_feedback(
                msg.get("query", ""),
                msg["content"],
                False,
                "",
            )
            st.rerun()


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------

def main() -> None:
    render_sidebar()

    st.title("AI Tools Knowledge Base — RAG Assistant")

    tab_chat, tab_telemetry = st.tabs(["💬 Chat", "📊 Telemetry"])

    with tab_chat:
        render_chat_tab()

    with tab_telemetry:
        render_telemetry_tab()


if __name__ == "__main__":
    main()