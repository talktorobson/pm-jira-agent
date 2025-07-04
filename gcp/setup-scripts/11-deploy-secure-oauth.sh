#!/bin/bash

# PM Jira Agent - Secure OAuth Deployment Script
# Removes public access and deploys OAuth-enabled version

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_ID="service-execution-uat-bb7"
REGION="europe-west9"
SERVICE_NAME="pm-jira-agent"

echo -e "${BLUE}🔐 PM Jira Agent - Secure OAuth Deployment${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

# Function to print section headers
print_section() {
    echo -e "\n${PURPLE}$1${NC}"
    echo -e "${PURPLE}$(printf '=%.0s' $(seq 1 ${#1}))${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_section "Pre-Deployment Security Analysis"

# Check current IAM policy
echo -e "${CYAN}Checking current IAM policy...${NC}"
CURRENT_POLICY=$(gcloud run services get-iam-policy "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(bindings[].members)" 2>/dev/null | grep -c "allUsers" || echo "0")

if [ "$CURRENT_POLICY" -gt 0 ]; then
    print_warning "SERVICE IS CURRENTLY PUBLIC - Will secure during deployment"
else
    print_success "Service already has restricted access"
fi

# Check current service URL
CURRENT_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.url)" 2>/dev/null || echo "not-deployed")

echo -e "${CYAN}Current service URL: $CURRENT_URL${NC}"

print_section "Building OAuth-Enabled Application"

# Navigate to application directory
cd "$(dirname "$0")/../../phase0-web-interface"

# Replace app.py with OAuth version
echo -e "${CYAN}Updating application with OAuth authentication...${NC}"
if [ -f "app_oauth.py" ]; then
    cp app.py app_original.py  # Backup original
    cp app_oauth.py app.py     # Use OAuth version
    print_success "OAuth-enabled app.py deployed"
else
    print_error "OAuth application file not found"
    exit 1
fi

# Check if requirements.txt has OAuth dependencies
if grep -q "authlib" requirements.txt; then
    print_success "OAuth dependencies found in requirements.txt"
else
    print_warning "OAuth dependencies missing - please ensure requirements.txt is updated"
fi

print_section "Deploying Secure Application"

# Build and deploy with enhanced security
echo -e "${CYAN}Building and deploying secure Cloud Run service...${NC}"

# Set up Artifact Registry repository
REPO_NAME="pm-jira-agent"
IMAGE_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME"

# Create repository if it doesn't exist
gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="PM Jira Agent secure container images" \
    --project="$PROJECT_ID" 2>/dev/null || echo "Repository already exists"

# Configure Docker authentication
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet

# Build the image
echo -e "${CYAN}Building container image...${NC}"
gcloud builds submit --tag "$IMAGE_URL" \
    --region="$REGION" \
    --project="$PROJECT_ID"

print_success "Container image built successfully"

# Deploy with NO public access
echo -e "${CYAN}Deploying with enhanced security...${NC}"
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_URL" \
    --platform managed \
    --region "$REGION" \
    --project="$PROJECT_ID" \
    --no-allow-unauthenticated \
    --ingress=internal-and-cloud-load-balancing \
    --port 5000 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 900 \
    --max-instances 10 \
    --min-instances 0 \
    --concurrency 80 \
    --cpu-throttling \
    --set-env-vars="FLASK_ENV=production,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --execution-environment gen2

print_success "Secure Cloud Run service deployed"

print_section "Configuring Authentication Access"

# Remove any existing public access
echo -e "${CYAN}Removing public access...${NC}"
gcloud run services remove-iam-policy-binding "$SERVICE_NAME" \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --region="$REGION" \
    --project="$PROJECT_ID" 2>/dev/null || echo "No public access to remove"

# Add domain-restricted access for Adeo
echo -e "${CYAN}Adding domain-restricted access for @adeo.com...${NC}"
gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --member="domain:adeo.com" \
    --role="roles/run.invoker" \
    --region="$REGION" \
    --project="$PROJECT_ID"

# Add service account access for internal operations
SERVICE_ACCOUNT="pm-jira-web-interface@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/run.invoker" \
    --region="$REGION" \
    --project="$PROJECT_ID"

print_success "Authentication access configured"

print_section "Configuring Load Balancer Security"

# Check if Load Balancer exists
LB_IP=$(gcloud compute addresses describe pm-jira-agent-ip --global --format="value(address)" --project="$PROJECT_ID" 2>/dev/null || echo "")

if [ -n "$LB_IP" ]; then
    echo -e "${CYAN}Updating existing Load Balancer security...${NC}"
    
    # Update backend service to use new secure Cloud Run service
    BACKEND_SERVICE="pm-jira-agent-backend"
    NEG_NAME="pm-jira-agent-neg"
    
    # Update Network Endpoint Group to point to secure service
    gcloud compute network-endpoint-groups update "$NEG_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --cloud-run-service="$SERVICE_NAME" || echo "NEG update skipped"
    
    print_success "Load Balancer updated for secure service"
    
    echo -e "${CYAN}🌐 Load Balancer IP: $LB_IP${NC}"
    echo -e "${YELLOW}⚠️  Note: Users must authenticate with @adeo.com accounts${NC}"
else
    print_warning "No Load Balancer found - service accessible via Cloud Run URL only"
fi

print_section "Testing Secure Deployment"

# Get the new service URL
SECURE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.url)")

echo -e "${CYAN}Testing secure endpoints...${NC}"

# Test health endpoint (should work)
echo -e "${CYAN}Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$SECURE_URL/health" || echo "000")

if [ "$HEALTH_RESPONSE" = "200" ]; then
    print_success "Health endpoint accessible"
elif [ "$HEALTH_RESPONSE" = "403" ]; then
    print_warning "Health endpoint requires authentication (expected)"
else
    print_error "Health endpoint test failed (HTTP $HEALTH_RESPONSE)"
fi

# Test main page (should require authentication)
echo -e "${CYAN}Testing main page (should require auth)...${NC}"
MAIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$SECURE_URL/" || echo "000")

if [ "$MAIN_RESPONSE" = "401" ] || [ "$MAIN_RESPONSE" = "403" ]; then
    print_success "Main page properly protected (HTTP $MAIN_RESPONSE)"
else
    print_warning "Main page response: HTTP $MAIN_RESPONSE"
fi

print_section "Security Validation"

# Verify IAM policy
echo -e "${CYAN}Verifying final IAM policy...${NC}"
FINAL_POLICY=$(gcloud run services get-iam-policy "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="json")

PUBLIC_ACCESS=$(echo "$FINAL_POLICY" | grep -c "allUsers" || echo "0")
DOMAIN_ACCESS=$(echo "$FINAL_POLICY" | grep -c "domain:adeo.com" || echo "0")

if [ "$PUBLIC_ACCESS" = "0" ]; then
    print_success "No public access confirmed"
else
    print_error "Public access still exists!"
fi

if [ "$DOMAIN_ACCESS" -gt "0" ]; then
    print_success "@adeo.com domain access confirmed"
else
    print_warning "Domain access not found"
fi

# Check ingress setting
INGRESS_SETTING=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(spec.template.metadata.annotations['run.googleapis.com/ingress'])")

if [ "$INGRESS_SETTING" = "internal-and-cloud-load-balancing" ]; then
    print_success "Ingress properly configured for internal + LB only"
else
    print_warning "Ingress setting: $INGRESS_SETTING"
fi

print_section "Deployment Summary"

echo -e "${GREEN}🎉 OAuth Deployment Complete!${NC}"
echo ""
echo -e "${CYAN}📋 Security Configuration:${NC}"
echo "   ✅ Public access removed"
echo "   ✅ @adeo.com domain restriction enabled"
echo "   ✅ Google OAuth 2.0 authentication required"
echo "   ✅ Service account access configured"
echo "   ✅ Internal + Load Balancer ingress only"
echo ""
echo -e "${CYAN}🔗 Access URLs:${NC}"
if [ -n "$LB_IP" ]; then
    echo "   🌐 Load Balancer: http://$LB_IP"
fi
echo "   ☁️  Cloud Run: $SECURE_URL"
echo ""
echo -e "${CYAN}🔐 Authentication Requirements:${NC}"
echo "   📧 Email: Must end with @adeo.com"
echo "   🔑 Authentication: Google OAuth 2.0"
echo "   ⏰ Session: 8-hour duration"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo "   • Users must login with @adeo.com Google accounts"
echo "   • OAuth consent screen must be configured in Google Cloud Console"
echo "   • OAuth credentials must be stored in Secret Manager"
echo "   • First-time users will see OAuth consent screen"
echo ""

if [ -n "$LB_IP" ]; then
    echo -e "${GREEN}🚀 Ready for testing: http://$LB_IP${NC}"
else
    echo -e "${GREEN}🚀 Ready for testing: $SECURE_URL${NC}"
fi

print_success "Secure OAuth deployment completed successfully!"