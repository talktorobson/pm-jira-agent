#!/bin/bash

# Debug secrets to check if they're working
PROJECT_ID="service-execution-uat-bb7"

echo "🔍 Debugging secrets..."
echo "Project: $PROJECT_ID"

echo ""
echo "📚 GitBook API Key (first 20 chars):"
gcloud secrets versions access latest --secret="gitbook-api-key" | head -c 20
echo "..."

echo ""
echo "🎫 Jira API Token (first 20 chars):"
gcloud secrets versions access latest --secret="jira-api-token" | head -c 20  
echo "..."

echo ""
echo "📧 Jira Email:"
gcloud secrets versions access latest --secret="jira-email"

echo ""
echo "🧪 Testing GitBook API directly..."
GITBOOK_KEY=$(gcloud secrets versions access latest --secret="gitbook-api-key")

echo "Testing user endpoint (auth verification):"
curl -H "Authorization: Bearer $GITBOOK_KEY" https://api.gitbook.com/v1/user | head -c 200

echo ""
echo "Testing spaces endpoint:"
curl -H "Authorization: Bearer $GITBOOK_KEY" https://api.gitbook.com/v1/spaces | head -c 200

echo ""
echo "Testing specific space:"
curl -H "Authorization: Bearer $GITBOOK_KEY" https://api.gitbook.com/v1/spaces/Jw57BieQciFYoCHgwVlm | head -c 200

echo ""
echo ""
echo "🧪 Testing Jira API directly with Bearer token..."
JIRA_TOKEN=$(gcloud secrets versions access latest --secret="jira-api-token")
curl -X GET "https://jira.adeo.com/rest/api/2/myself" \
  -H "Authorization: Bearer $JIRA_TOKEN" \
  -H "Content-Type: application/json" | head -c 200