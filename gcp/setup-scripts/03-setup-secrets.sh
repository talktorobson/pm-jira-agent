#!/bin/bash

# Setup GCP Secret Manager secrets for PM Jira Agent
# Project: service-execution-uat-bb7

PROJECT_ID="service-execution-uat-bb7"

echo "🔐 Setting up Secret Manager secrets..."
echo "Project: $PROJECT_ID"

# Set project
gcloud config set project $PROJECT_ID

# Create secrets (you'll need to add the actual values)
echo "📝 Creating secrets..."

echo "1. GitBook API Key"
echo "Please enter your GitBook API key:"
read -s GITBOOK_API_KEY
echo $GITBOOK_API_KEY | gcloud secrets create gitbook-api-key --data-file=-

echo "2. Jira API Token"
echo "Please enter your Jira API token:"
read -s JIRA_API_TOKEN
echo $JIRA_API_TOKEN | gcloud secrets create jira-api-token --data-file=-

echo "3. Jira Email"
echo "Please enter your Jira email address:"
read JIRA_EMAIL
echo $JIRA_EMAIL | gcloud secrets create jira-email --data-file=-

# Grant access to service account
SERVICE_ACCOUNT_EMAIL="pm-jira-agent@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔑 Granting access to service account..."
gcloud secrets add-iam-policy-binding gitbook-api-key \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding jira-api-token \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding jira-email \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

echo "✅ Secrets setup completed!"
echo ""
echo "Created secrets:"
echo "- gitbook-api-key"
echo "- jira-api-token"
echo "- jira-email"
echo ""
echo "Next steps:"
echo "1. Run: ./04-deploy-functions.sh"