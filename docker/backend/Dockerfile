# Stage 1: Builder
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Create and activate a virtual environment
RUN uv venv /app/.venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies first (Layer Caching)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy source code and install the project itself
COPY src ./src
RUN uv sync --frozen --no-dev


# Stage 2: Runtime
FROM python:3.11-slim-bookworm

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the pre-built virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY src ./src

# Copy ML artifacts required by the API
COPY models ./models
COPY data/processed ./data/processed
COPY data/raw/ratings.dat ./data/raw/ratings.dat

# Expose API Port
EXPOSE 8000

# Define Start Command using the Uvicorn binary directly from the virtual environment
CMD ["uvicorn", "lumiere.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]