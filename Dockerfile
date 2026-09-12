# Use selenium's standalone Chrome image (pre-configured for headless)
FROM selenium/standalone-chrome:120.0.6099.109

# Switch to root to install Python dependencies
USER root

WORKDIR /app

# Install Python and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create directories with proper permissions
RUN mkdir -p /app/logs /app/state /app/chrome_profiles \
    && chown -R seluser:seluser /app

# Copy application code
COPY --chown=seluser:seluser . .

# Switch back to seluser
USER seluser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

ENTRYPOINT ["python", "farmer.py"]
CMD ["--wallets", "10"]