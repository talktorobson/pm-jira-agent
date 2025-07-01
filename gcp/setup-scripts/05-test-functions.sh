#!/bin/bash

# Test Cloud Functions for PM Jira Agent
# Project: service-execution-uat-bb7
# Region: europe-west9

PROJECT_ID="service-execution-uat-bb7"
REGION="europe-west9"

echo "🧪 Testing Cloud Functions..."

# Get function URLs
GITBOOK_FUNCTION_URL=$(gcloud functions describe gitbook-api --gen2 --region=$REGION --format="value(serviceConfig.uri)")
JIRA_FUNCTION_URL=$(gcloud functions describe jira-api --gen2 --region=$REGION --format="value(serviceConfig.uri)")

echo "📚 Testing GitBook API function..."
echo "URL: $GITBOOK_FUNCTION_URL"

# Test GitBook content retrieval
curl -X POST "$GITBOOK_FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get_content"
  }' | jq .

echo ""
echo "🎫 Testing Jira API function..."
echo "URL: $JIRA_FUNCTION_URL"

# Test Jira tickets retrieval
curl -X POST "$JIRA_FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "get_tickets",
    "jql": "project = AHSSI ORDER BY created DESC",
    "max_results": 5
  }' | jq .

echo ""
echo "✅ Function testing completed!"
echo ""
echo "If tests passed, proceed to:"
echo "1. Run: ./06-setup-vertex-ai.sh"