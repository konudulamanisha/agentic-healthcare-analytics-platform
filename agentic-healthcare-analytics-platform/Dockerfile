# ── Agentic Healthcare Analytics Platform ──────────────────────
# Multi-stage Docker build for production FastAPI deployment
# ───────────────────────────────────────────────────────────────

FROM python:3.12-slim AS base

LABEL maintainer="Manisha Konudula"
LABEL description="Agentic Healthcare Analytics Platform — LangGraph + FastAPI"
LABEL version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# ── Dependencies ───────────────────────────────────────────────
FROM base AS deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Application ────────────────────────────────────────────────
FROM deps AS app
COPY src/       ./src/
COPY data/      ./data/
COPY output/    ./output/

RUN mkdir -p /app/output

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run FastAPI via uvicorn
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
