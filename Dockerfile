# Lightweight Python image - no browser needed
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN groupadd -r farmer && useradd -r -g farmer farmer \
    && mkdir -p /app/logs /app/state \
    && chown -R farmer:farmer /app

# Copy application code
COPY --chown=farmer:farmer . .

USER farmer

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

ENTRYPOINT ["python", "farmer.py"]
CMD ["--wallets", "10"]