# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.12.20 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
WORKDIR /app
RUN useradd --create-home --uid 10001 app
COPY --from=builder /app/.venv /app/.venv
COPY ats_checker.py ./
COPY models/ ./models/
COPY prompts/ ./prompts/
COPY services/ ./services/
COPY utils/ ./utils/
USER app
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"]
CMD ["python", "-m", "streamlit", "run", "ats_checker.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
