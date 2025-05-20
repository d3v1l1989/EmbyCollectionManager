# Dockerfile for TMDbCollector
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
COPY .env.example ./

# Expose config volume for mounting secrets/configs
VOLUME ["/app/config"]

# Default command: show help
CMD ["python", "-m", "src.app_logic", "--help"]
