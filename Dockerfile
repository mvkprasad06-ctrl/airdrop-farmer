# Multi-stage Dockerfile for Airdrop Farmer
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl gnupg2 unzip fontconfig \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Ensure chromedriver is in PATH
RUN ln -sf /usr/bin/chromium-driver /usr/local/bin/chromedriver \
    && ln -sf /usr/bin/chromium /usr/bin/google-chrome

FROM base AS deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

FROM base AS final
WORKDIR /app
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
RUN groupadd -r farmer && useradd -r -g farmer farmer \
    && mkdir -p /app/logs /app/state /app/chrome_profiles \
    && chown -R farmer:farmer /app
COPY --chown=farmer:farmer . .
USER farmer
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CHROME_HEADLESS=true \
    DISPLAY=:99
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"
ENTRYPOINT ["python", "farmer.py"]
CMD ["--wallets", "10"]