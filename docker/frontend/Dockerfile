# Stage 1: Builder
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Create and activate a virtual environment
RUN uv venv /app/.venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (Layer Caching)
RUN uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime
FROM python:3.11-slim-bookworm

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# UPDATED: Copy UI source code
COPY src/lumiere/ui ./src/lumiere/ui

# Expose Streamlit default port
EXPOSE 8501

# Healthcheck to ensure UI is running (Using Python instead of curl)
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# UPDATED: Define Start Command for Streamlit with correct path
CMD ["python", "-m", "streamlit", "run", "src/lumiere/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]