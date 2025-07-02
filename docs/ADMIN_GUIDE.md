# 🔒 Administrator Guide

**System management, monitoring, and maintenance for PM Jira Agent**

---

## 🎯 Overview

### Administrator Responsibilities

- **System Health**: Monitor performance and availability
- **User Management**: Control access and permissions
- **Configuration**: Manage business rules and settings
- **Security**: Maintain authentication and authorization
- **Troubleshooting**: Resolve system issues and user problems
- **Updates**: Deploy new versions and features

### System Architecture

```
PM Jira Agent Production System
├── Google Cloud Platform
│   ├── Vertex AI (Multi-Agent System)
│   ├── Cloud Functions (API Gateway)
│   ├── Secret Manager (Credentials)
│   ├── Cloud Monitoring (Observability)
│   └── Cloud Logging (Audit Trail)
├── External Integrations
│   ├── Jira API (Ticket Creation)
│   └── GitBook API (Documentation Research)
└── Business Rules Engine (Compliance)
```

---

## 📊 System Monitoring

### Key Performance Indicators

| Metric | Target | Alert Threshold | Action Required |
|--------|--------|-----------------|----------------|
| **Uptime** | 99.9% | <99.5% | Investigate immediately |
| **Response Time** | <3s | >5s | Performance optimization |
| **Quality Score** | >0.8 | <0.75 avg | Review business rules |
| **Success Rate** | >95% | <90% | System health check |
| **API Errors** | <1% | >5% | Check integrations |

### Monitoring Dashboard

**Access Google Cloud Console:**
1. Go to [Cloud Monitoring](https://console.cloud.google.com/monitoring)
2. Navigate to Dashboards → PM Jira Agent
3. Review key metrics and alerts

**Custom Metrics:**
```bash
# View workflow metrics
gcloud monitoring metrics list --filter="metric.type:custom.googleapis.com/pm_jira_agent/*"

# Check recent performance
gcloud monitoring metrics-descriptors list --filter="pm_jira_agent"
```

### Alert Configuration

**Critical Alerts:**
```yaml
# alerting-policy.yaml
alerting_policies:
  - display_name: "PM Jira Agent - System Down"
    conditions:
      - display_name: "Health check failing"
        condition_threshold:
          filter: 'resource.type="cloud_function"'
          comparison: COMPARISON_GREATER_THAN
          threshold_value: 5
          duration: 300s
    notification_channels: ["slack-webhook", "email-alerts"]
    severity: CRITICAL

  - display_name: "PM Jira Agent - High Response Time"
    conditions:
      - display_name: "Slow response times"
        condition_threshold:
          filter: 'metric.type="custom.googleapis.com/pm_jira_agent/workflow_duration"'
          comparison: COMPARISON_GREATER_THAN
          threshold_value: 10
          duration: 180s
    notification_channels: ["email-alerts"]
    severity: WARNING
```

---

## 👥 User Management

### Access Control

**User Roles:**
- **Business Users**: Create tickets via API
- **Administrators**: Full system access
- **Developers**: Technical integration access
- **Viewers**: Read-only monitoring access

**API Key Management:**
```bash
# Generate new API key
API_KEY=$(openssl rand -hex 32)
echo $API_KEY

# Store in Secret Manager
echo $API_KEY | gcloud secrets create api-key-user-$(date +%Y%m%d) --data-file=-

# Grant access to specific users
gcloud secrets add-iam-policy-binding api-key-user-20250702 \
  --member="user:user@company.com" \
  --role="roles/secretmanager.secretAccessor"
```

**User Onboarding Checklist:**
- [ ] Create user account in GCP project
- [ ] Assign appropriate IAM roles
- [ ] Generate API key
- [ ] Provide user documentation
- [ ] Conduct training session
- [ ] Test access with sample request

### Permission Matrix

| Role | Create Tickets | View Logs | Modify Config | Deploy Updates | Monitor System |
|------|---------------|-----------|--------------|---------------|--------------|
| **Business User** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Developer** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Administrator** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Viewer** | ❌ | ✅ | ❌ | ❌ | ✅ |

---

## ⚙️ Configuration Management

### Business Rules Configuration

**Current Rules Location:**
```python
# gcp/agent-configs/business_rules.py
BUSINESS_RULES = {
    "ui_ux_rules": {
        "accessibility": "Must comply with WCAG 2.1 AA standards",
        "responsive_design": "Must work on mobile and desktop",
        "performance": "Page load time must be <3 seconds"
    },
    "security_compliance": {
        "authentication": "All user data access requires authentication",
        "authorization": "Role-based access control required",
        "data_protection": "PII must be encrypted at rest and in transit"
    },
    "development_standards": {
        "testing": "Unit tests required for all new features",
        "documentation": "API changes must be documented",
        "code_review": "All changes require peer review"
    }
}
```

**Adding New Rules:**
```python
# 1. Edit business_rules.py
# 2. Add new rule category
BUSINESS_RULES["compliance_gdpr"] = {
    "data_retention": "User data must be deletable within 30 days",
    "consent": "Explicit consent required for data processing",
    "data_portability": "User data must be exportable"
}

# 3. Deploy changes
./gcp/setup-scripts/04-deploy-functions.sh
```

### System Configuration

**Environment Variables:**
```bash
# View current configuration
gcloud secrets list --filter="name~pm-jira-agent"

# Update configuration
echo "new-config-value" | gcloud secrets versions add config-setting --data-file=-

# Verify update
gcloud secrets versions access latest --secret="config-setting"
```

**Agent Configuration:**
```python
# Update agent parameters
AGENT_CONFIG = {
    "quality_threshold": 0.8,      # Minimum quality score
    "max_iterations": 3,           # Maximum improvement cycles
    "timeout_seconds": 30,         # Agent timeout
    "model_temperature": 0.3,      # AI creativity level
    "max_tokens": 4000             # Response length limit
}
```

---

## 🔒 Security Management

### Authentication & Authorization

**Service Account Audit:**
```bash
# Review service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:pm-jira-agent@*" \
  --format="table(bindings.role,bindings.members)"

# Check for overprivileged accounts
gcloud projects get-iam-policy $PROJECT_ID \
  --format="json" | jq '.bindings[] | select(.role | contains("admin"))'
```

**API Security:**
```python
# Security middleware implementation
class SecurityMiddleware:
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        # Rate limiting
        if self.is_rate_limited(environ):
            return self.rate_limit_response(start_response)
        
        # API key validation
        if not self.validate_api_key(environ):
            return self.auth_error_response(start_response)
        
        # Input sanitization
        environ = self.sanitize_input(environ)
        
        return self.app(environ, start_response)
```

**Security Checklist:**
- [ ] API keys rotated regularly (every 90 days)
- [ ] Service account permissions minimal
- [ ] All secrets stored in Secret Manager
- [ ] Input validation enabled
- [ ] Rate limiting configured
- [ ] Audit logging enabled
- [ ] HTTPS enforced for all endpoints
- [ ] Regular security scans performed

### Secret Rotation

```bash
#!/bin/bash
# rotate-secrets.sh

echo "Starting secret rotation..."

# Rotate Jira API token
echo "Enter new Jira API token:"
read -s NEW_JIRA_TOKEN
echo $NEW_JIRA_TOKEN | gcloud secrets versions add jira-api-token --data-file=-

# Test new token
python3 -c "from tools import call_jira_api; print(call_jira_api('get_tickets', {}))"

if [ $? -eq 0 ]; then
    echo "Jira token rotation successful"
else
    echo "Jira token rotation failed - rolling back"
    # Rollback logic here
fi

# Rotate GitBook API key
echo "Enter new GitBook API key:"
read -s NEW_GITBOOK_KEY
echo $NEW_GITBOOK_KEY | gcloud secrets versions add gitbook-api-key --data-file=-

# Test new key
python3 -c "from tools import call_gitbook_api; print(call_gitbook_api('search', {'query': 'test'}))"

echo "Secret rotation completed"
```

---

## 🔧 Troubleshooting

### Common Issues

#### **Issue: Low Quality Scores**

**Symptoms:**
- Average quality score <0.8
- High iteration count
- User complaints about ticket rejections

**Diagnosis:**
```bash
# Check recent quality scores
gcloud logging read 'jsonPayload.quality_score<0.8' --limit=20

# Analyze rejection patterns
python3 -c "
import json
from collections import Counter

# Load recent workflow logs
logs = []  # Load from Cloud Logging
rejection_reasons = [log['rejection_reason'] for log in logs if 'rejection_reason' in log]
print(Counter(rejection_reasons))
"
```

**Solutions:**
1. Review and update business rules
2. Provide better user training
3. Adjust quality threshold temporarily
4. Update prompt templates

#### **Issue: High Response Times**

**Symptoms:**
- Response times >5 seconds
- User timeouts
- Performance alerts

**Diagnosis:**
```bash
# Check function execution times
gcloud functions logs read --limit=50 --format=json | \
  jq '.[] | select(.severity=="INFO" and .jsonPayload.execution_time) | 
     {timestamp: .timestamp, execution_time: .jsonPayload.execution_time}'

# Monitor concurrent executions
gcloud monitoring metrics list --filter="metric.type:cloudfunctions.googleapis.com/function/executions"
```

**Solutions:**
1. Increase function memory allocation
2. Optimize AI model parameters
3. Implement request caching
4. Scale Cloud Function instances

#### **Issue: API Integration Failures**

**Symptoms:**
- Jira/GitBook API errors
- Authentication failures
- Network timeouts

**Diagnosis:**
```bash
# Check API error rates
gcloud logging read 'jsonPayload.api_error=true' --limit=20

# Test API connectivity
curl -H "Authorization: Bearer $(gcloud secrets versions access latest --secret=jira-api-token)" \
     "https://jira.adeo.com/rest/api/2/myself"
```

**Solutions:**
1. Verify API credentials
2. Check rate limits
3. Update API endpoints
4. Implement retry logic

### Diagnostic Commands

```bash
# System health overview
python3 health_check.py

# Recent error analysis
gcloud logging read 'severity>=ERROR' --limit=20 --format=json

# Performance metrics
gcloud monitoring metrics list --filter="pm_jira_agent" | head -10

# User activity analysis
gcloud logging read 'jsonPayload.user_request' --limit=50 | \
  grep -o '"user":"[^"]*"' | sort | uniq -c

# Quality score trends
python3 -c "
import pandas as pd
from google.cloud import logging

# Fetch quality scores from last 7 days
# Generate trend analysis
print('Quality score trend analysis...')
"
```

---

## 🚀 Deployment & Updates

### Deployment Pipeline

**Production Deployment Process:**
1. **Development Testing**: All tests pass locally
2. **Staging Deployment**: Deploy to staging environment
3. **Integration Testing**: Full end-to-end tests
4. **Performance Validation**: Load testing and benchmarks
5. **Security Review**: Security scan and audit
6. **Production Deployment**: Blue-green deployment
7. **Post-deployment Monitoring**: 24-hour observation period

**Automated Deployment:**
```bash
#!/bin/bash
# automated-deploy.sh

set -e

echo "Starting automated deployment pipeline..."

# 1. Run tests
echo "Running tests..."
pytest tests/ --cov=. --cov-report=term-missing

# 2. Security scan
echo "Running security scan..."
bandit -r gcp/agent-configs/

# 3. Deploy to staging
echo "Deploying to staging..."
export ENVIRONMENT=staging
./gcp/setup-scripts/04-deploy-functions.sh

# 4. Run integration tests
echo "Running integration tests..."
python3 integration_tests.py

# 5. Deploy to production
echo "Deploying to production..."
export ENVIRONMENT=production
./gcp/setup-scripts/04-deploy-functions.sh

# 6. Verify deployment
echo "Verifying deployment..."
curl -f https://your-function-url/health || exit 1

echo "Deployment completed successfully!"
```

### Rollback Procedures

**Immediate Rollback:**
```bash
#!/bin/bash
# emergency-rollback.sh

echo "EMERGENCY ROLLBACK INITIATED"

# Get previous working revision
PREV_REVISION=$(gcloud functions list --filter="name:pm-jira-agent" \
  --format="value(updateTime)" | sort | tail -2 | head -1)

# Rollback each function
functions=("jira-api" "gitbook-api")
for func in "${functions[@]}"; do
  echo "Rolling back $func..."
  gcloud functions deploy $func --source=./backup/last-known-good/
done

# Verify rollback
for func in "${functions[@]}"; do
  curl -f "https://$func-hash.region.r.appspot.com/health" || echo "$func rollback failed"
done

echo "Rollback completed. Verify system functionality."
```

**Version Management:**
```bash
# Tag current version before deployment
git tag -a v1.2.3 -m "Release version 1.2.3"
git push origin v1.2.3

# Create backup of current deployment
mkdir -p backups/v1.2.3
cp -r gcp/agent-configs backups/v1.2.3/

# Document deployment
echo "$(date): Deployed version 1.2.3" >> deployment-log.txt
```

---

## 📈 Performance Optimization

### Resource Optimization

**Cloud Function Tuning:**
```bash
# Analyze function performance
gcloud functions logs read jira-api --limit=100 | \
  grep "Function execution took" | \
  awk '{print $NF}' | \
  sort -n

# Optimize memory allocation
gcloud functions deploy jira-api \
  --memory=512Mi \
  --timeout=120s \
  --max-instances=10
```

**AI Model Optimization:**
```python
# Optimize model parameters for performance
OPTIMAL_CONFIG = {
    "model_name": "gemini-2.5-flash",  # Fastest model
    "temperature": 0.2,               # Focused responses
    "max_tokens": 2000,               # Reasonable limit
    "timeout": 25,                    # Quick timeout
    "streaming": False                # Batch processing
}

# Implement response caching
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_ai_request(prompt_hash, model_config):
    """Cache frequently requested prompts"""
    return ai_model.generate(prompt, config=model_config)
```

### Scaling Configuration

**Auto-scaling Settings:**
```yaml
# scaling-config.yaml
cloud_functions:
  jira-api:
    min_instances: 0
    max_instances: 20
    concurrency: 1000
    memory: 256Mi
    
  gitbook-api:
    min_instances: 0
    max_instances: 10
    concurrency: 1000
    memory: 256Mi

vertex_ai:
  prediction_endpoint:
    min_replica_count: 1
    max_replica_count: 10
    machine_type: "n1-standard-2"
```

---

## 📁 Backup & Recovery

### Data Backup Strategy

**What to Backup:**
1. **Configuration**: Business rules, agent settings
2. **Secrets**: API keys, credentials (encrypted)
3. **Code**: Application source code
4. **Logs**: System logs and audit trails (retention policy)
5. **Metrics**: Performance and usage data

**Backup Script:**
```bash
#!/bin/bash
# backup-system.sh

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$BACKUP_DATE"

mkdir -p $BACKUP_DIR

echo "Starting system backup to $BACKUP_DIR..."

# 1. Export configuration
gcloud secrets list --format="value(name)" > $BACKUP_DIR/secrets-list.txt

# 2. Backup source code
cp -r gcp/ $BACKUP_DIR/

# 3. Export monitoring configuration
gcloud alpha monitoring policies list --format=json > $BACKUP_DIR/monitoring-policies.json

# 4. Export function configurations
gcloud functions list --format=json > $BACKUP_DIR/functions-config.json

# 5. Backup business rules
cp gcp/agent-configs/business_rules.py $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

### Disaster Recovery

**Recovery Procedures:**
1. **Complete System Failure**: Redeploy from backup
2. **Partial Service Outage**: Restart affected components
3. **Data Corruption**: Restore from last known good backup
4. **Security Incident**: Isolate, assess, recover

**Recovery Script:**
```bash
#!/bin/bash
# disaster-recovery.sh

RECOVERY_DATE=$1
if [ -z "$RECOVERY_DATE" ]; then
  echo "Usage: $0 <backup-date>"
  echo "Available backups:"
  ls -1 backups/
  exit 1
fi

BACKUP_DIR="backups/$RECOVERY_DATE"

echo "Starting disaster recovery from $BACKUP_DIR..."

# 1. Restore source code
cp -r $BACKUP_DIR/gcp ./

# 2. Redeploy functions
cd gcp/setup-scripts
./04-deploy-functions.sh

# 3. Restore monitoring
gcloud alpha monitoring policies create --policy-from-file=$BACKUP_DIR/monitoring-policies.json

# 4. Verify recovery
python3 ../agent-configs/test_workflow.py

echo "Disaster recovery completed. Verify all systems operational."
```

---

## 📞 Support & Escalation

### Support Tiers

**Tier 1 - User Support:**
- User training and guidance
- Basic troubleshooting
- API key management
- Documentation updates

**Tier 2 - Technical Support:**
- System configuration issues
- Performance optimization
- Integration problems
- Security concerns

**Tier 3 - Engineering Support:**
- System architecture changes
- Major bug fixes
- Security incidents
- Disaster recovery

### Escalation Procedures

**Severity Levels:**

| Severity | Description | Response Time | Escalation |
|----------|-------------|---------------|------------|
| **P0 - Critical** | System down, data loss | 15 minutes | Immediate |
| **P1 - High** | Major functionality broken | 2 hours | 4 hours |
| **P2 - Medium** | Feature degraded | 8 hours | 24 hours |
| **P3 - Low** | Minor issues, feature requests | 48 hours | 1 week |

**Contact Information:**
```yaml
contacts:
  primary_admin: "admin@company.com"
  technical_lead: "tech-lead@company.com"
  security_team: "security@company.com"
  on_call: "+1-xxx-xxx-xxxx"
  
escalation_matrix:
  p0_critical:
    immediate: ["primary_admin", "on_call"]
    15_min: ["technical_lead", "management"]
    30_min: ["security_team", "external_support"]
    
  p1_high:
    immediate: ["primary_admin"]
    4_hours: ["technical_lead"]
    24_hours: ["management"]
```

### Documentation Maintenance

**Regular Updates:**
- [ ] Monthly system health report
- [ ] Quarterly security review
- [ ] Semi-annual disaster recovery test
- [ ] Annual architecture review

**Change Management:**
1. Document all configuration changes
2. Update runbooks after incidents
3. Maintain up-to-date contact information
4. Review and update procedures quarterly

---

**System Administration Complete! Your PM Jira Agent is production-ready with enterprise-grade monitoring and support! 🚀**