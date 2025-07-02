#!/bin/bash
set -e

echo "🤖 Starting PM Jira Agent Phase 0"
echo "=================================="
echo "Port: ${PORT:-5000}"
echo "Environment: ${FLASK_ENV:-production}"
echo "Project: ${GOOGLE_CLOUD_PROJECT:-service-execution-uat-bb7}"
echo ""

# Create default config if none exists
if [ ! -f /app/config/config.yaml ]; then
    echo "📄 Creating default configuration..."
    cp /app/config/config.yaml.template /app/config/config.yaml
fi

# Start the application
echo "🚀 Starting Flask application..."
exec python app.py