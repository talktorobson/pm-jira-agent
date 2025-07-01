#!/bin/bash

# Enable required GCP APIs for PM Jira Agent
# Project: service-execution-uat-bb7
# Region: europe-west9

PROJECT_ID="service-execution-uat-bb7"
REGION="europe-west9"

echo "🚀 Enabling required APIs for PM Jira Agent..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
echo "📡 Enabling Vertex AI API..."
gcloud services enable aiplatform.googleapis.com

echo "⚡ Enabling Cloud Functions API..."
gcloud services enable cloudfunctions.googleapis.com

echo "🔐 Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

echo "🏃 Enabling Cloud Run API..."
gcloud services enable run.googleapis.com

echo "🔨 Enabling Cloud Build API..."
gcloud services enable cloudbuild.googleapis.com

echo "📦 Enabling Artifact Registry API..."
gcloud services enable artifactregistry.googleapis.com

echo "✅ All APIs enabled successfully!"
echo ""
echo "Next steps:"
echo "1. Run: ./02-setup-iam.sh"
echo "2. Run: ./03-setup-secrets.sh"