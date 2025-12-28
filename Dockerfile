FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev \
    ffmpeg libsm6 libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.18 /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock README.md /app/

# Copy the application code into the container
COPY documentapp /app/documentapp
COPY mysite /app/mysite
COPY manage.py /app/manage.py

# Install dependencies
RUN uv sync --frozen --no-dev
