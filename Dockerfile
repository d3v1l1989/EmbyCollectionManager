# Dockerfile for Emby Collection Manager
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py ./
COPY config/ ./config/
COPY resources/ ./resources/

# Create traktlists directory for user-defined collections
RUN mkdir -p /app/traktlists

# Expose volumes for mounting configs and user lists
VOLUME ["/app/config", "/app/traktlists"]

# Add entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD []
