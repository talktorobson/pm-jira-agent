#!/bin/bash

# PM Jira Agent - Security Implementation Script
# This script implements Cloud IAM authentication for Cloud Functions

set -e

PROJECT_ID="service-execution-uat-bb7"
REGION="europe-west9"
SERVICE_ACCOUNT_NAME="pm-jira-web-interface"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔒 Starting PM Jira Agent Security Implementation..."

# Set the active project
gcloud config set project $PROJECT_ID

echo "📋 Step 1: Removing public access from Cloud Functions..."

# Remove allUsers IAM binding from GitBook API
echo "  - Removing public access from gitbook-api..."
gcloud run services remove-iam-policy-binding gitbook-api \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region=$REGION \
  --quiet || echo "    Warning: allUsers binding may not exist"

# Remove allUsers IAM binding from Jira API
echo "  - Removing public access from jira-api..."
gcloud run services remove-iam-policy-binding jira-api \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region=$REGION \
  --quiet || echo "    Warning: allUsers binding may not exist"

echo "📋 Step 2: Creating dedicated service account for web interface..."

# Create service account for web interface
echo "  - Creating service account: $SERVICE_ACCOUNT_NAME..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --display-name="PM Jira Agent Web Interface" \
  --description="Service account for Phase 0 web interface to access Cloud Functions" \
  --quiet || echo "    Warning: Service account may already exist"

echo "📋 Step 3: Granting Cloud Run Invoker permissions..."

# Grant invoker role for GitBook API
echo "  - Granting invoker permission for gitbook-api..."
gcloud run services add-iam-policy-binding gitbook-api \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="roles/run.invoker" \
  --region=$REGION \
  --quiet

# Grant invoker role for Jira API
echo "  - Granting invoker permission for jira-api..."
gcloud run services add-iam-policy-binding jira-api \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="roles/run.invoker" \
  --region=$REGION \
  --quiet

echo "📋 Step 4: Creating service account key for authentication..."

# Create and download service account key
echo "  - Creating service account key..."
gcloud iam service-accounts keys create "../../phase0-web-interface/service-account-key.json" \
  --iam-account=$SERVICE_ACCOUNT_EMAIL \
  --quiet

echo "📋 Step 5: Verifying security configuration..."

# Check current IAM policies
echo "  - Verifying GitBook API access..."
gcloud run services get-iam-policy gitbook-api --region=$REGION

echo "  - Verifying Jira API access..."
gcloud run services get-iam-policy jira-api --region=$REGION

echo "✅ Security implementation completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Update Phase 0 web interface to use service account authentication"
echo "2. Test authenticated access to verify security"
echo "3. Update deployment scripts to maintain security"
echo ""
echo "🔑 Service Account Details:"
echo "  Name: $SERVICE_ACCOUNT_NAME"
echo "  Email: $SERVICE_ACCOUNT_EMAIL"
echo "  Key File: phase0-web-interface/service-account-key.json"
echo ""
echo "⚠️  IMPORTANT: The service account key file contains sensitive credentials."
echo "   Ensure it's added to .gitignore and handled securely."