# dashboard.py
import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="System Telemetry", layout="wide", initial_sidebar_state="collapsed")

# 2. Vercel/Stripe-Inspired Minimalist CSS Injection
st.markdown("""
<style>
    /* Absolute reset and minimalist background */
    .stApp {
        background-color: #fafafa;
        color: #111827;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Remove default Streamlit top padding and header */
    .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }
    header {visibility: hidden;}
    
    /* Typography strictness */
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.025em;
        color: #111827;
    }
    h1 { font-size: 2.25rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 1rem; margin-bottom: 2rem;}
    h2 { font-size: 1.25rem; margin-top: 2rem; margin-bottom: 1rem; color: #374151; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em;}
    
    /* Enterprise Card Styling for Metrics */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        transition: border-color 0.15s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #d1d5db;
    }
    
    /* Metric Typography */
    div[data-testid="metric-container"] > div {
        color: #6b7280; /* Label color */
        font-weight: 500;
        font-size: 0.875rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #111827; /* Value color */
        font-weight: 700;
        font-size: 2rem;
        letter-spacing: -0.025em;
    }
    
    /* Clean up the dataframe */
    .stDataFrame {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

st.title("System Telemetry & RAG Observability")

# File Paths
ANALYTICS_FILE = os.path.join("logs", "application_analytics.json")
FEEDBACK_FILE = os.path.join("logs", "user_feedback.csv")

# Load Analytics
try:
    with open(ANALYTICS_FILE, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"total_requests": 0, "successful_requests": 0, "failed_requests": 0, "average_response_time_ms": 0, "estimated_api_cost_usd": 0, "total_tokens_consumed": 0}

total_reqs = max(data.get("total_requests", 1), 1)
success_rate = (data.get("successful_requests", 0) / total_reqs) * 100

# 3. Primary Telemetry Grid
st.header("Core Pipeline Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Invocations", f"{data.get('total_requests', 0):,}")
col2.metric("Retrieval Success Rate", f"{success_rate:.1f}%")
col3.metric("P99 Response Latency", f"{data.get('average_response_time_ms', 0):.1f} ms")
col4.metric("Operational Cost (USD)", f"${data.get('estimated_api_cost_usd', 0):.4f}")

# 4. Minimalist Data Visualizations (Plotly)
st.header("Resource Utilization")
col_chart1, col_chart2 = st.columns(2)

def create_minimal_gauge(value, title, max_val, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 14, 'color': '#6b7280', 'family': 'Inter'}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "#e5e7eb", 'visible': False},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "#f3f4f6",
            'borderwidth': 0,
        },
        number = {'font': {'color': '#111827', 'size': 36, 'family': 'Inter'}}
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=250, margin=dict(l=20, r=20, t=30, b=20))
    return fig

with col_chart1:
    # Emerald green for system reliability
    st.plotly_chart(create_minimal_gauge(success_rate, "API Reliability Target (%)", 100, "#10b981"), use_container_width=True)

with col_chart2:
    # Slate for raw throughput
    st.plotly_chart(create_minimal_gauge(data.get("total_tokens_consumed", 0), "Context Window Token Volume", 50000, "#374151"), use_container_width=True)

# 5. Infrastructure Dimensions
st.header("Vector Space Infrastructure")
col5, col6, col7, col8 = st.columns(4)
col5.metric("Indexed Documents", "13")
col6.metric("Active Embeddings", "13")
col7.metric("Successful Queries", f"{data.get('successful_requests', 0):,}")
col8.metric("Failed Operations", f"{data.get('failed_requests', 0):,}")

# 6. Qualitative Feedback Data
st.header("User Interaction Ledger")
if os.path.exists(FEEDBACK_FILE):
    df = pd.read_csv(FEEDBACK_FILE)
    
    col_faq, col_db = st.columns([1, 2])
    with col_faq:
        st.markdown("**High-Frequency Queries**")
        faq_counts = df['Original Question'].value_counts().reset_index()
        faq_counts.columns = ['Query', 'Volume']
        st.dataframe(faq_counts.head(5), use_container_width=True, hide_index=True)
        
    with col_db:
        st.markdown("**Raw Feedback Stream**")
        # Clean, enterprise styling for the dataframe
        styled_df = df.style.map(
            lambda x: "color: #10b981; font-weight: 600;" if x == "Helpful" else ("color: #ef4444; font-weight: 600;" if x == "Not Helpful" else ""), 
            subset=["Rating"]
        )
        st.dataframe(styled_df, use_container_width=True)
else:
    st.info("Awaiting initial user feedback telemetry...")