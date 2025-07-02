# Phase 0 PM Jira Agent - Web Interface
# Single-stage build for simplicity and reliability

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies globally
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create user after installing packages (so packages are available globally)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/config /app/logs /app/static \
    && chown -R appuser:appuser /app

# Copy default configuration if it doesn't exist
COPY config/config.yaml.template /app/config/config.yaml.template

# Environment variables with defaults
ENV FLASK_ENV=production
ENV PORT=5000
ENV SECRET_KEY=change-me-in-production
ENV GOOGLE_CLOUD_PROJECT=service-execution-uat-bb7

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh && chown appuser:appuser /app/start.sh

# Expose port
EXPOSE ${PORT}

# Switch to non-root user
USER appuser

# Run the application
CMD ["/app/start.sh"]

# Labels for container metadata
LABEL maintainer="PM Jira Agent Team"
LABEL version="0.1.0"
LABEL description="Phase 0 Web Interface for PM Jira Agent"
LABEL phase="0"