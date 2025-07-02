# 🔧 Technical Setup Guide

**Complete implementation and deployment guide for PM Jira Agent**

---

## 🎯 Overview

### Architecture

```
PM Jira Agent System
├── Vertex AI Multi-Agent System
│   ├── PM Agent (Gemini 2.5 Flash)
│   ├── Tech Lead Agent (Gemini 2.5 Flash)
│   └── Jira Creator Agent (Gemini 2.5 Flash)
├── Business Rules Engine
├── Google Cloud Functions (API Layer)
│   ├── GitBook API Integration
│   └── Jira API Integration
├── GCP Secret Manager (Credentials)
└── Monitoring & Analytics
```

### Tech Stack

- **AI Platform**: Google Cloud Vertex AI
- **AI Models**: Gemini 2.5 Flash (latest)
- **Runtime**: Python 3.11
- **Cloud Functions**: Gen2, europe-west9
- **Authentication**: GCP Service Accounts + Secret Manager
- **APIs**: Jira REST API, GitBook API
- **Monitoring**: Google Cloud Logging + Custom Analytics

---

## 🛠️ Prerequisites

### Required Accounts & Access

1. **Google Cloud Platform**
   - Project with billing enabled
   - Admin or Editor permissions
   - Vertex AI API access

2. **Jira Instance**
   - Admin access to create API tokens
   - Project creation permissions
   - User account for agent integration

3. **GitBook (Optional)**
   - Workspace access
   - API token generation permissions

### Local Development Environment

```bash
# Required tools
python3.11+
git
gcloud CLI
curl (for testing)

# Python packages
pip install google-cloud-aiplatform
pip install google-cloud-secret-manager
pip install google-cloud-functions-framework
pip install requests
pip install flask
```

---

## 🚀 Quick Setup

### 1. Clone and Prepare

```bash
# Clone repository
git clone https://github.com/talktorobson/pm-jira-agent.git
cd pm-jira-agent

# Setup Python environment
cd gcp/agent-configs
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. GCP Project Setup

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export REGION="europe-west9"

# Run automated setup scripts
cd ../setup-scripts

# Enable APIs
./01-enable-apis.sh

# Setup IAM and service accounts
./02-setup-iam.sh

# Configure secrets (you'll be prompted for API keys)
./03-setup-secrets.sh

# Deploy cloud functions
./04-deploy-functions.sh

# Test the deployment
./05-test-functions.sh
```

### 3. Vertex AI Agent Setup

```bash
# Deploy the multi-agent system
./10-enhanced-production-deployment.sh

# Test end-to-end workflow
cd ../agent-configs
python3 test_workflow.py
```

### 4. Validation

```bash
# Test complete system
python3 -c "
from orchestrator import create_jira_ticket_with_ai
result = create_jira_ticket_with_ai('Test deployment - add simple login validation')
print('Success!' if result.get('success') else 'Failed!')
print('Ticket:', result.get('ticket_url', 'Not created'))
"
```

If you see a ticket URL, setup is complete! 🎉

---

## 🔍 Detailed Setup

### GCP Project Configuration

#### Required APIs
```bash
# Core APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable serviceusage.googleapis.com

# Additional APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
```

#### Service Account Setup
```bash
# Create service account
gcloud iam service-accounts create pm-jira-agent \
  --display-name="PM Jira Agent Service Account" \
  --description="Service account for PM Jira Agent system"

# Assign required roles
roles=(
  "roles/aiplatform.user"
  "roles/cloudfunctions.developer"
  "roles/secretmanager.secretAccessor"
  "roles/logging.logWriter"
  "roles/monitoring.metricWriter"
)

for role in "${roles[@]}"; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:pm-jira-agent@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="$role"
done
```

### Secret Manager Configuration

```bash
# Create secrets
gcloud secrets create jira-api-token --data-file=-
# Paste your Jira API token when prompted

gcloud secrets create jira-email --data-file=-
# Paste your Jira email when prompted

gcloud secrets create gitbook-api-key --data-file=-
# Paste your GitBook API key when prompted (optional)

# Grant access to service account
secrets=("jira-api-token" "jira-email" "gitbook-api-key")
for secret in "${secrets[@]}"; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:pm-jira-agent@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

### Cloud Functions Deployment

#### Jira API Function
```bash
cd gcp/cloud-functions/jira-api

# Deploy function
gcloud functions deploy jira-api \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=jira_api \
  --trigger=https \
  --memory=256Mi \
  --timeout=60s \
  --service-account=pm-jira-agent@$PROJECT_ID.iam.gserviceaccount.com \
  --allow-unauthenticated
```

#### GitBook API Function
```bash
cd ../gitbook-api

# Deploy function
gcloud functions deploy gitbook-api \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=gitbook_api \
  --trigger=https \
  --memory=256Mi \
  --timeout=60s \
  --service-account=pm-jira-agent@$PROJECT_ID.iam.gserviceaccount.com \
  --allow-unauthenticated
```

### Vertex AI Agent Configuration

```python
# gcp/agent-configs/config.py
PROJECT_ID = "your-project-id"
REGION = "europe-west9"
MODEL_NAME = "gemini-2.5-flash"  # Latest model

# Agent configuration
AGENT_CONFIG = {
    "pm_agent": {
        "model": MODEL_NAME,
        "temperature": 0.3,
        "max_tokens": 4000,
        "timeout": 30
    },
    "tech_lead_agent": {
        "model": MODEL_NAME,
        "temperature": 0.2,
        "max_tokens": 3000,
        "timeout": 25
    },
    "jira_creator_agent": {
        "model": MODEL_NAME,
        "temperature": 0.1,
        "max_tokens": 2000,
        "timeout": 20
    }
}

# Quality thresholds
QUALITY_THRESHOLD = 0.8
MAX_ITERATIONS = 3

# API endpoints
JIRA_FUNCTION_URL = "https://jira-api-{hash}.{region}.r.appspot.com"
GITBOOK_FUNCTION_URL = "https://gitbook-api-{hash}.{region}.r.appspot.com"
```

---

## 🗺️ Environment Configuration

### Development Environment

```bash
# .env.development
PROJECT_ID=your-dev-project
REGION=europe-west9
ENVIRONMENT=development
LOG_LEVEL=DEBUG
QUALITY_THRESHOLD=0.75
TEST_MODE=true
```

### Production Environment

```bash
# .env.production
PROJECT_ID=your-prod-project
REGION=europe-west9
ENVIRONMENT=production
LOG_LEVEL=INFO
QUALITY_THRESHOLD=0.8
TEST_MODE=false
MONITORING_ENABLED=true
ALERT_WEBHOOK_URL=your-slack-webhook
```

### Environment Variables

```python
# Load environment configuration
import os
from dotenv import load_dotenv

load_dotenv(f'.env.{os.getenv("ENVIRONMENT", "development")}')

class Config:
    PROJECT_ID = os.getenv('PROJECT_ID')
    REGION = os.getenv('REGION', 'europe-west9')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    QUALITY_THRESHOLD = float(os.getenv('QUALITY_THRESHOLD', '0.8'))
    MAX_ITERATIONS = int(os.getenv('MAX_ITERATIONS', '3'))
    TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'
    MONITORING_ENABLED = os.getenv('MONITORING_ENABLED', 'false').lower() == 'true'
```

---

## 🔍 Testing & Validation

### Unit Tests

```python
# tests/test_agents.py
import pytest
from orchestrator import PMAgent, TechLeadAgent, JiraCreatorAgent

class TestPMAgent:
    def test_simple_request(self):
        agent = PMAgent()
        result = agent.process_request("Add user login")
        assert result['success'] == True
        assert 'user_story' in result
        assert 'acceptance_criteria' in result
    
    def test_quality_scoring(self):
        agent = PMAgent()
        result = agent.process_request(
            "Add comprehensive user authentication with OAuth 2.0"
        )
        assert result['quality_score'] >= 0.8

class TestTechLeadAgent:
    def test_technical_review(self):
        agent = TechLeadAgent()
        ticket_draft = {
            "summary": "Add OAuth authentication",
            "description": "Implement secure login"
        }
        result = agent.review_ticket(ticket_draft)
        assert 'technical_feasibility' in result
        assert 'quality_score' in result

class TestWorkflow:
    def test_end_to_end(self):
        from orchestrator import create_jira_ticket_with_ai
        result = create_jira_ticket_with_ai(
            "Add password reset functionality"
        )
        assert result['success'] == True
        assert 'ticket_key' in result
        assert result['quality_metrics']['final_quality_score'] >= 0.8
```

### Integration Tests

```python
# tests/test_integration.py
import pytest
from tools import call_jira_api, call_gitbook_api

class TestAPIIntegration:
    def test_jira_connection(self):
        result = call_jira_api("get_tickets", {})
        assert result['success'] == True
        assert 'tickets' in result
    
    def test_gitbook_connection(self):
        result = call_gitbook_api("search", {"query": "authentication"})
        assert result['success'] == True
        assert 'results' in result
    
    def test_ticket_creation(self):
        ticket_data = {
            "summary": "Test ticket creation",
            "description": "This is a test ticket",
            "issue_type": "Task"
        }
        result = call_jira_api("create_ticket", ticket_data)
        assert result['success'] == True
        assert 'ticket_key' in result
```

### Performance Tests

```python
# tests/test_performance.py
import time
import pytest
from orchestrator import create_jira_ticket_with_ai

class TestPerformance:
    def test_response_time(self):
        start_time = time.time()
        result = create_jira_ticket_with_ai("Add simple search feature")
        execution_time = time.time() - start_time
        
        assert result['success'] == True
        assert execution_time < 5.0  # Should complete in under 5 seconds
    
    def test_concurrent_requests(self):
        import concurrent.futures
        
        requests = [
            "Add user profile page",
            "Fix login button styling", 
            "Improve search performance",
            "Add notification preferences"
        ]
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(create_jira_ticket_with_ai, req) for req in requests]
            results = [future.result() for future in futures]
        execution_time = time.time() - start_time
        
        assert all(r['success'] for r in results)
        assert execution_time < 10.0  # Parallel execution should be efficient
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run specific test categories
pytest tests/test_agents.py -v
pytest tests/test_integration.py -v
pytest tests/test_performance.py -v

# Run tests with detailed output
pytest -v -s tests/
```

---

## 📊 Monitoring & Observability

### Logging Configuration

```python
# monitoring.py
import logging
from google.cloud import logging as cloud_logging
from google.cloud.logging.handlers import CloudLoggingHandler

class MonitoringSetup:
    def __init__(self, project_id, environment):
        self.project_id = project_id
        self.environment = environment
        self.setup_logging()
    
    def setup_logging(self):
        client = cloud_logging.Client(project=self.project_id)
        handler = CloudLoggingHandler(client)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[handler, logging.StreamHandler()]
        )
        
        self.logger = logging.getLogger('pm-jira-agent')
    
    def log_workflow_start(self, workflow_id, user_request):
        self.logger.info(
            "Workflow started",
            extra={
                "workflow_id": workflow_id,
                "user_request": user_request,
                "environment": self.environment
            }
        )
    
    def log_agent_execution(self, agent_name, execution_time, result):
        self.logger.info(
            f"{agent_name} execution completed",
            extra={
                "agent": agent_name,
                "execution_time": execution_time,
                "success": result.get('success', False),
                "quality_score": result.get('quality_score', 0)
            }
        )
    
    def log_error(self, error_message, context):
        self.logger.error(
            error_message,
            extra={
                "error_context": context,
                "environment": self.environment
            }
        )
```

### Custom Metrics

```python
# metrics.py
from google.cloud import monitoring_v3
import time

class MetricsCollector:
    def __init__(self, project_id):
        self.project_id = project_id
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"
    
    def record_workflow_duration(self, duration_seconds):
        series = monitoring_v3.TimeSeries()
        series.metric.type = "custom.googleapis.com/pm_jira_agent/workflow_duration"
        series.resource.type = "global"
        
        point = monitoring_v3.Point()
        point.value.double_value = duration_seconds
        point.interval.end_time.seconds = int(time.time())
        series.points = [point]
        
        self.client.create_time_series(
            name=self.project_name,
            time_series=[series]
        )
    
    def record_quality_score(self, quality_score):
        series = monitoring_v3.TimeSeries()
        series.metric.type = "custom.googleapis.com/pm_jira_agent/quality_score"
        series.resource.type = "global"
        
        point = monitoring_v3.Point()
        point.value.double_value = quality_score
        point.interval.end_time.seconds = int(time.time())
        series.points = [point]
        
        self.client.create_time_series(
            name=self.project_name,
            time_series=[series]
        )
```

### Health Checks

```python
# health_check.py
from flask import Flask, jsonify
from tools import call_jira_api, call_gitbook_api
import time

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Comprehensive health check endpoint"""
    checks = {
        'system': check_system_health(),
        'jira_api': check_jira_connection(),
        'gitbook_api': check_gitbook_connection(),
        'vertex_ai': check_vertex_ai(),
        'timestamp': int(time.time())
    }
    
    overall_health = all(check['status'] == 'healthy' for check in checks.values() if isinstance(check, dict))
    
    response = {
        'status': 'healthy' if overall_health else 'unhealthy',
        'checks': checks
    }
    
    return jsonify(response), 200 if overall_health else 503

def check_system_health():
    return {'status': 'healthy', 'message': 'System operational'}

def check_jira_connection():
    try:
        result = call_jira_api('get_tickets', {'limit': 1})
        return {
            'status': 'healthy' if result.get('success') else 'unhealthy',
            'message': 'Jira API accessible' if result.get('success') else 'Jira API error'
        }
    except Exception as e:
        return {'status': 'unhealthy', 'message': f'Jira connection failed: {str(e)}'}

def check_gitbook_connection():
    try:
        result = call_gitbook_api('search', {'query': 'test', 'limit': 1})
        return {
            'status': 'healthy' if result.get('success') else 'unhealthy',
            'message': 'GitBook API accessible' if result.get('success') else 'GitBook API error'
        }
    except Exception as e:
        return {'status': 'unhealthy', 'message': f'GitBook connection failed: {str(e)}'}

def check_vertex_ai():
    try:
        from orchestrator import PMAgent
        agent = PMAgent()
        # Simple test to verify AI model access
        result = agent.process_request("Test system health")
        return {
            'status': 'healthy' if result.get('success') else 'unhealthy',
            'message': 'Vertex AI accessible' if result.get('success') else 'Vertex AI error'
        }
    except Exception as e:
        return {'status': 'unhealthy', 'message': f'Vertex AI connection failed: {str(e)}'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

---

## 🔒 Security Configuration

### API Security

```python
# security.py
import hmac
import hashlib
import time
from functools import wraps
from flask import request, jsonify

class SecurityManager:
    def __init__(self, api_key_secret):
        self.api_key_secret = api_key_secret
    
    def validate_api_key(self, provided_key):
        """Validate API key using secure comparison"""
        expected_key = self.api_key_secret
        return hmac.compare_digest(provided_key.encode(), expected_key.encode())
    
    def require_api_key(self, f):
        """Decorator to require API key authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key or not self.validate_api_key(api_key):
                return jsonify({'error': 'Invalid API key'}), 401
            return f(*args, **kwargs)
        return decorated_function
    
    def rate_limit_check(self, identifier, limit=100, window=3600):
        """Simple rate limiting implementation"""
        # Implementation would use Redis or similar for production
        # This is a simplified version
        current_time = int(time.time())
        window_start = current_time - window
        
        # In production, store and check request counts per identifier
        # Return True if under limit, False if over limit
        return True  # Simplified for example
```

### Input Validation

```python
# validation.py
from marshmallow import Schema, fields, validate, ValidationError

class TicketRequestSchema(Schema):
    user_request = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=2000),
        error_messages={'required': 'User request is required'}
    )
    priority = fields.Str(
        validate=validate.OneOf(['Low', 'Medium', 'High', 'Critical']),
        missing='Medium'
    )
    issue_type = fields.Str(
        validate=validate.OneOf(['Story', 'Task', 'Bug', 'Epic']),
        missing='Story'
    )
    context = fields.Dict(
        missing={},
        validate=validate.Length(max=10)  # Limit context fields
    )

def validate_ticket_request(data):
    """Validate incoming ticket request data"""
    schema = TicketRequestSchema()
    try:
        return schema.load(data)
    except ValidationError as e:
        raise ValueError(f"Validation error: {e.messages}")

def sanitize_input(text):
    """Sanitize user input to prevent injection attacks"""
    if not isinstance(text, str):
        return str(text)
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'", '`']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Limit length
    return text[:2000]
```

---

## 🚀 Deployment Strategies

### Production Deployment

```bash
#!/bin/bash
# deploy-production.sh

set -e

echo "Starting production deployment..."

# Set production environment
export ENVIRONMENT=production
export PROJECT_ID="your-prod-project"
export REGION="europe-west9"

# Deploy cloud functions
echo "Deploying cloud functions..."
cd gcp/setup-scripts
./04-deploy-functions.sh

# Deploy Vertex AI agents
echo "Deploying Vertex AI agents..."
./10-enhanced-production-deployment.sh

# Run production tests
echo "Running production validation..."
cd ../agent-configs
python3 production_test.py

# Health check
echo "Performing health checks..."
curl -f http://localhost:8080/health || exit 1

echo "Production deployment completed successfully!"
```

### Blue-Green Deployment

```bash
#!/bin/bash
# blue-green-deploy.sh

# Deploy to green environment
echo "Deploying to green environment..."
export ENVIRONMENT=green
./deploy-production.sh

# Run comprehensive tests
echo "Running green environment tests..."
python3 comprehensive_tests.py

# Switch traffic to green
echo "Switching traffic to green environment..."
gcloud run services update-traffic pm-jira-agent \
  --to-latest \
  --region=$REGION

echo "Blue-green deployment completed!"
```

### Rollback Strategy

```bash
#!/bin/bash
# rollback.sh

echo "Starting rollback to previous version..."

# Get previous revision
PREVIOUS_REVISION=$(gcloud run revisions list \
  --service=pm-jira-agent \
  --region=$REGION \
  --limit=2 \
  --sort-by=~metadata.creationTimestamp \
  --format="value(metadata.name)" | tail -1)

# Rollback traffic
gcloud run services update-traffic pm-jira-agent \
  --to-revisions=$PREVIOUS_REVISION=100 \
  --region=$REGION

echo "Rollback completed to revision: $PREVIOUS_REVISION"
```

---

## 📁 Configuration Management

### Environment-Specific Configs

```python
# config/production.py
class ProductionConfig:
    PROJECT_ID = "your-prod-project"
    REGION = "europe-west9"
    ENVIRONMENT = "production"
    
    # AI Model settings
    MODEL_NAME = "gemini-2.5-flash"
    QUALITY_THRESHOLD = 0.8
    MAX_ITERATIONS = 3
    
    # Performance settings
    TIMEOUT_SECONDS = 30
    MAX_CONCURRENT_REQUESTS = 10
    RETRY_ATTEMPTS = 3
    
    # Monitoring
    LOG_LEVEL = "INFO"
    MONITORING_ENABLED = True
    ALERT_WEBHOOK = "https://hooks.slack.com/your-webhook"
    
    # Security
    API_KEY_REQUIRED = True
    RATE_LIMIT_ENABLED = True
    CORS_ENABLED = False
```

```python
# config/development.py
class DevelopmentConfig:
    PROJECT_ID = "your-dev-project"
    REGION = "europe-west9"
    ENVIRONMENT = "development"
    
    # AI Model settings (relaxed for development)
    MODEL_NAME = "gemini-2.5-flash"
    QUALITY_THRESHOLD = 0.7  # Lower threshold for testing
    MAX_ITERATIONS = 2
    
    # Performance settings
    TIMEOUT_SECONDS = 60  # Longer timeout for debugging
    MAX_CONCURRENT_REQUESTS = 5
    RETRY_ATTEMPTS = 1
    
    # Monitoring
    LOG_LEVEL = "DEBUG"
    MONITORING_ENABLED = False
    ALERT_WEBHOOK = None
    
    # Security (relaxed for development)
    API_KEY_REQUIRED = False
    RATE_LIMIT_ENABLED = False
    CORS_ENABLED = True
```

---

## 📞 Support & Troubleshooting

### Common Issues

#### "Permission denied" errors
```bash
# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:pm-jira-agent@$PROJECT_ID.iam.gserviceaccount.com"

# Re-assign required roles if missing
./gcp/setup-scripts/02-setup-iam.sh
```

#### "Model not found" errors
```python
# Verify Vertex AI model availability
from google.cloud import aiplatform

aiplatform.init(project=PROJECT_ID, location=REGION)
models = aiplatform.Model.list()
print([m.display_name for m in models if 'gemini' in m.display_name.lower()])
```

#### "API timeout" errors
```bash
# Check Cloud Function logs
gcloud functions logs read jira-api --region=$REGION --limit=50
gcloud functions logs read gitbook-api --region=$REGION --limit=50

# Increase timeout if needed
gcloud functions deploy jira-api --timeout=120s --region=$REGION
```

### Debug Commands

```bash
# System health check
python3 -c "from health_check import health_check; print(health_check())"

# Test individual components
python3 -c "from tools import call_jira_api; print(call_jira_api('get_tickets', {}))"
python3 -c "from tools import call_gitbook_api; print(call_gitbook_api('search', {'query': 'test'}))"

# View recent logs
gcloud logging read "resource.type=cloud_function" --limit=20 --format=json

# Check API quotas
gcloud compute project-info describe --format="table(quotas.metric,quotas.usage,quotas.limit)"
```

### Support Contacts

- **Technical Issues**: Check GitHub issues or internal documentation
- **GCP Platform Issues**: Google Cloud Support
- **Jira API Issues**: Atlassian Support
- **GitBook API Issues**: GitBook Support

---

**Setup complete! Your PM Jira Agent system is ready for production use! 🚀**