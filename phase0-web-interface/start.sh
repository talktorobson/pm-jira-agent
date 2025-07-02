#!/bin/bash
set -e

echo "🤖 Starting PM Jira Agent Phase 0"
echo "=================================="
echo "Port: ${PORT:-5000}"
echo "Environment: ${FLASK_ENV:-production}"
echo "Project: ${GOOGLE_CLOUD_PROJECT:-service-execution-uat-bb7}"
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo ""

# Verify Python packages
echo "🔍 Checking Python packages..."
python -c "import flask, flask_socketio, yaml" || {
    echo "❌ Missing required Python packages"
    echo "Available packages:"
    pip list | head -10
    exit 1
}

# Test if our app can be imported
echo "🔍 Testing app import..."
python -c "
import sys
sys.path.insert(0, '/app')
try:
    from app import app
    print('✅ App imported successfully')
except Exception as e:
    print(f'❌ App import failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

# Create necessary directories
mkdir -p /app/config /app/logs /app/static

# Create default config if none exists
if [ ! -f /app/config/config.yaml ]; then
    echo "📄 Creating default configuration..."
    if [ -f /app/config/config.yaml.template ]; then
        cp /app/config/config.yaml.template /app/config/config.yaml
    else
        echo "⚠️ No config template found, creating minimal config..."
        cat > /app/config/config.yaml << 'EOF'
user_info:
  name: "Product Manager"
  email: "pm@company.com"
  team: "Product Team"
jira:
  base_url: "https://yourcompany.atlassian.net"
  project_key: "PROJ"
  default_issue_type: "Story"
  default_priority: "Medium"
gitbook:
  enabled: false
custom_prompts:
  company_context: "Technology company"
  writing_style: "professional"
business_rules:
  ui_ux_guidelines: "Follow modern UI/UX best practices"
  security_requirements: "All user data must be secure"
  performance_standards: "Optimize for fast user experience"
EOF
    fi
fi

# Set environment variables for Cloud Run
export PORT=${PORT:-5000}
export FLASK_ENV=${FLASK_ENV:-production}
export GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-service-execution-uat-bb7}

# Start the application
echo "🚀 Starting Flask application on port $PORT..."
echo "📁 Config file exists: $([ -f /app/config/config.yaml ] && echo 'YES' || echo 'NO')"

# For simplicity and reliability, use Flask's built-in server
# Note: While not ideal for heavy production loads, it's sufficient for Phase 0 individual instances
echo "🚀 Starting Flask application directly..."
exec python app.py