# Step 1: Base image with Python 3.11 and uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Step 2: Set the Working Directory
WORKDIR /app

# Step 3: Configure uv behavior for Docker environments
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Step 4: Install dependencies first (Leveraging Docker layer caching)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev

# Step 5: Copy the application source code
COPY src ./src

# Step 6: Install the project package itself
RUN uv sync --frozen --no-dev

# Step 7: Expose API Port
EXPOSE 8000

# Step 8: Define Start Command
CMD ["uv", "run", "uvicorn", "lumiere.api.main:app", "--host", "0.0.0.0", "--port", "8000"]