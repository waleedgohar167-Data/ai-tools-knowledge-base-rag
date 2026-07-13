# ==========================================
# STAGE 1: BUILDER
# ==========================================
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
# Ultra-resilient pip install for network drops
RUN pip install --default-timeout=1000 --retries=10 -r requirements.txt

# ==========================================
# STAGE 2: RUNNER (Production)
# ==========================================
FROM python:3.12-slim

WORKDIR /app

# Create a non-root user for security
RUN useradd -m -r appuser && \
    chown appuser /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code and set ownership
COPY --chown=appuser:appuser . .

# Switch to the secure non-root user
USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py"]