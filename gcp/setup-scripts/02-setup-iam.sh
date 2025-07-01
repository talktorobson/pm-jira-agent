#!/bin/bash

# Setup IAM roles and service accounts for PM Jira Agent
# Project: service-execution-uat-bb7

PROJECT_ID="service-execution-uat-bb7"
SERVICE_ACCOUNT_NAME="pm-jira-agent"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔐 Setting up IAM for PM Jira Agent..."
echo "Project: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"

# Set project
gcloud config set project $PROJECT_ID

# Create service account
echo "👤 Creating service account..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --description="Service account for PM Jira Agent" \
    --display-name="PM Jira Agent Service Account"

# Assign roles
echo "🎭 Assigning roles..."

echo "  - Vertex AI User"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/aiplatform.user"

echo "  - Cloud Functions Developer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/cloudfunctions.developer"

echo "  - Secret Manager Accessor"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

echo "  - Cloud Run Developer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/run.developer"

echo "  - Cloud Build Editor"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/cloudbuild.builds.editor"

echo "✅ IAM setup completed!"
echo ""
echo "Service Account Email: $SERVICE_ACCOUNT_EMAIL"
echo ""
echo "Next steps:"
echo "1. Run: ./03-setup-secrets.sh"
echo "2. Run: ./04-deploy-functions.sh"