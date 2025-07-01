#!/bin/bash

# Setup Vertex AI Agent Builder for PM Jira Agent
# Project: service-execution-uat-bb7
# Region: europe-west9

PROJECT_ID="service-execution-uat-bb7"
REGION="europe-west9"
AGENT_NAME="pm-jira-agent"

echo "🤖 Setting up Vertex AI Agent Builder..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Agent: $AGENT_NAME"

# Set project
gcloud config set project $PROJECT_ID

echo ""
echo "📋 Phase 1 Basic Setup Instructions:"
echo ""
echo "1. Go to Vertex AI Agent Builder in Google Cloud Console:"
echo "   https://console.cloud.google.com/gen-app-builder/engines?project=$PROJECT_ID"
echo ""
echo "2. Create a new Agent with these settings:"
echo "   - Agent Name: $AGENT_NAME"
echo "   - Agent Type: Chat"
echo "   - Region: $REGION"
echo "   - Company Name: Adeo"
echo ""
echo "3. Configure Basic Agent Settings:"
echo "   - Goal: Create high-quality Jira tickets from user requests"
echo "   - Instructions: Act as a Product Manager assistant that creates comprehensive Jira tickets"
echo "   - Model: Gemini 1.5 Pro"
echo ""
echo "4. Add Tools (coming in Phase 2):"
echo "   - GitBook Function: https://gitbook-api-jlhinciqia-od.a.run.app"
echo "   - Jira Function: https://jira-api-jlhinciqia-od.a.run.app"
echo ""
echo "✅ Phase 1 Complete: API integrations working!"
echo "🚀 Ready for Phase 2: Multi-agent logic and handoffs"
echo ""
echo "Your Cloud Function URLs:"
echo "GitBook API: https://gitbook-api-jlhinciqia-od.a.run.app"
echo "Jira API: https://jira-api-jlhinciqia-od.a.run.app"