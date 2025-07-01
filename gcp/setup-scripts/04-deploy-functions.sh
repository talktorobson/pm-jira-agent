#!/bin/bash

# Deploy Cloud Functions for PM Jira Agent
# Project: service-execution-uat-bb7
# Region: europe-west9

PROJECT_ID="service-execution-uat-bb7"
REGION="europe-west9"
SERVICE_ACCOUNT_EMAIL="pm-jira-agent@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🚀 Deploying Cloud Functions for PM Jira Agent..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Set project and region
gcloud config set project $PROJECT_ID
gcloud config set functions/region $REGION

# Deploy GitBook API function
echo "📚 Deploying GitBook API function..."
cd ../cloud-functions/gitbook-api
gcloud functions deploy gitbook-api \
    --gen2 \
    --runtime=python311 \
    --source=. \
    --entry-point=gitbook_api \
    --trigger-http \
    --allow-unauthenticated \
    --service-account=$SERVICE_ACCOUNT_EMAIL \
    --memory=256Mi \
    --timeout=60s \
    --max-instances=10

GITBOOK_FUNCTION_URL=$(gcloud functions describe gitbook-api --gen2 --region=$REGION --format="value(serviceConfig.uri)")
echo "GitBook Function URL: $GITBOOK_FUNCTION_URL"

# Deploy Jira API function
echo "🎫 Deploying Jira API function..."
cd ../jira-api
gcloud functions deploy jira-api \
    --gen2 \
    --runtime=python311 \
    --source=. \
    --entry-point=jira_api \
    --trigger-http \
    --allow-unauthenticated \
    --service-account=$SERVICE_ACCOUNT_EMAIL \
    --memory=256Mi \
    --timeout=60s \
    --max-instances=10

JIRA_FUNCTION_URL=$(gcloud functions describe jira-api --gen2 --region=$REGION --format="value(serviceConfig.uri)")
echo "Jira Function URL: $JIRA_FUNCTION_URL"

echo "✅ Cloud Functions deployed successfully!"
echo ""
echo "Function URLs:"
echo "GitBook API: $GITBOOK_FUNCTION_URL"
echo "Jira API: $JIRA_FUNCTION_URL"
echo ""
echo "Next steps:"
echo "1. Test the functions with: ./05-test-functions.sh"
echo "2. Setup Vertex AI Agent: ./06-setup-vertex-ai.sh"