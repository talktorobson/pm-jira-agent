#!/bin/bash

# PM Jira Agent - Google OAuth 2.0 Setup Script
# Sets up OAuth credentials and secrets for secure authentication

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
CLOUD_RUN_URL="https://pm-jira-agent-jlhinciqia-od.a.run.app"

echo -e "${BLUE}🔐 PM Jira Agent - Google OAuth 2.0 Setup${NC}"
echo -e "${BLUE}===========================================${NC}"
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

print_section "Setting up Google OAuth 2.0 Credentials"

echo -e "${CYAN}📋 OAuth Configuration Details:${NC}"
echo "   Project ID: $PROJECT_ID"
echo "   Cloud Run URL: $CLOUD_RUN_URL"
echo "   Redirect URI: $CLOUD_RUN_URL/auth/callback"
echo "   Domain Restriction: adeo.com"
echo ""

print_warning "MANUAL STEP REQUIRED: OAuth Consent Screen Setup"
echo -e "${CYAN}You need to set up OAuth consent screen manually in Google Cloud Console:${NC}"
echo ""
echo "1. Go to: https://console.cloud.google.com/apis/credentials/consent?project=$PROJECT_ID"
echo "2. Configure OAuth consent screen:"
echo "   - User Type: Internal"
echo "   - App Name: PM Jira Agent"
echo "   - User Support Email: robson.reis@adeo.com"
echo "   - Developer Contact: robson.reis@adeo.com"
echo "   - Authorized Domains: adeo.com"
echo ""

read -p "Press Enter after completing OAuth consent screen setup..."

print_warning "MANUAL STEP REQUIRED: OAuth Client Credentials"
echo -e "${CYAN}Create OAuth 2.0 Client ID in Google Cloud Console:${NC}"
echo ""
echo "1. Go to: https://console.cloud.google.com/apis/credentials?project=$PROJECT_ID"
echo "2. Click 'Create Credentials' → 'OAuth 2.0 Client ID'"
echo "3. Application Type: Web Application"
echo "4. Name: PM Jira Agent OAuth Client"
echo "5. Authorized JavaScript Origins:"
echo "   - $CLOUD_RUN_URL"
echo "   - https://localhost:5000 (for local testing)"
echo "6. Authorized Redirect URIs:"
echo "   - $CLOUD_RUN_URL/auth/callback"
echo "   - https://localhost:5000/auth/callback (for local testing)"
echo ""

read -p "Press Enter after creating OAuth client credentials..."

echo ""
print_warning "ENTER OAUTH CREDENTIALS"
echo -e "${CYAN}Please enter the OAuth credentials from the Google Cloud Console:${NC}"
echo ""

# Get OAuth Client ID
while [ -z "$OAUTH_CLIENT_ID" ]; do
    read -p "Enter OAuth Client ID: " OAUTH_CLIENT_ID
    if [ -z "$OAUTH_CLIENT_ID" ]; then
        print_error "Client ID is required"
    fi
done

# Get OAuth Client Secret
while [ -z "$OAUTH_CLIENT_SECRET" ]; do
    read -s -p "Enter OAuth Client Secret: " OAUTH_CLIENT_SECRET
    echo ""
    if [ -z "$OAUTH_CLIENT_SECRET" ]; then
        print_error "Client Secret is required"
    fi
done

print_section "Storing OAuth Credentials in Secret Manager"

# Store OAuth Client ID
echo -e "${CYAN}Storing OAuth Client ID...${NC}"
echo -n "$OAUTH_CLIENT_ID" | gcloud secrets create google-oauth-client-id \
    --data-file=- \
    --project="$PROJECT_ID" 2>/dev/null || \
echo -n "$OAUTH_CLIENT_ID" | gcloud secrets versions add google-oauth-client-id \
    --data-file=- \
    --project="$PROJECT_ID"

print_success "OAuth Client ID stored in Secret Manager"

# Store OAuth Client Secret
echo -e "${CYAN}Storing OAuth Client Secret...${NC}"
echo -n "$OAUTH_CLIENT_SECRET" | gcloud secrets create google-oauth-client-secret \
    --data-file=- \
    --project="$PROJECT_ID" 2>/dev/null || \
echo -n "$OAUTH_CLIENT_SECRET" | gcloud secrets versions add google-oauth-client-secret \
    --data-file=- \
    --project="$PROJECT_ID"

print_success "OAuth Client Secret stored in Secret Manager"

# Generate and store Flask secret key
echo -e "${CYAN}Generating Flask secret key...${NC}"
FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo -n "$FLASK_SECRET_KEY" | gcloud secrets create flask-secret-key \
    --data-file=- \
    --project="$PROJECT_ID" 2>/dev/null || \
echo -n "$FLASK_SECRET_KEY" | gcloud secrets versions add flask-secret-key \
    --data-file=- \
    --project="$PROJECT_ID"

print_success "Flask secret key generated and stored"

print_section "Configuring IAM Permissions for Secret Access"

# Grant service account access to secrets
echo -e "${CYAN}Configuring service account permissions...${NC}"

SERVICE_ACCOUNT="pm-jira-web-interface@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant access to OAuth Client ID
gcloud secrets add-iam-policy-binding google-oauth-client-id \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID"

# Grant access to OAuth Client Secret
gcloud secrets add-iam-policy-binding google-oauth-client-secret \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID"

# Grant access to Flask Secret Key
gcloud secrets add-iam-policy-binding flask-secret-key \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID"

print_success "Service account permissions configured"

print_section "Testing Secret Access"

# Test secret access
echo -e "${CYAN}Testing secret retrieval...${NC}"

# Test OAuth Client ID
CLIENT_ID_TEST=$(gcloud secrets versions access latest --secret="google-oauth-client-id" --project="$PROJECT_ID" 2>/dev/null)
if [ -n "$CLIENT_ID_TEST" ]; then
    print_success "OAuth Client ID retrieval: Working"
else
    print_error "OAuth Client ID retrieval: Failed"
fi

# Test OAuth Client Secret
CLIENT_SECRET_TEST=$(gcloud secrets versions access latest --secret="google-oauth-client-secret" --project="$PROJECT_ID" 2>/dev/null)
if [ -n "$CLIENT_SECRET_TEST" ]; then
    print_success "OAuth Client Secret retrieval: Working"
else
    print_error "OAuth Client Secret retrieval: Failed"
fi

# Test Flask Secret Key
FLASK_KEY_TEST=$(gcloud secrets versions access latest --secret="flask-secret-key" --project="$PROJECT_ID" 2>/dev/null)
if [ -n "$FLASK_KEY_TEST" ]; then
    print_success "Flask Secret Key retrieval: Working"
else
    print_error "Flask Secret Key retrieval: Failed"
fi

print_section "OAuth Setup Summary"

echo -e "${GREEN}✅ OAuth 2.0 Setup Complete!${NC}"
echo ""
echo -e "${CYAN}📋 Configuration Summary:${NC}"
echo "   OAuth Client ID: ${CLIENT_ID_TEST:0:20}...****"
echo "   OAuth Client Secret: ****"
echo "   Flask Secret Key: ****"
echo "   Redirect URI: $CLOUD_RUN_URL/auth/callback"
echo "   Domain Restriction: adeo.com"
echo ""
echo -e "${CYAN}🔗 Authorized URLs:${NC}"
echo "   Cloud Run: $CLOUD_RUN_URL"
echo "   Local Dev: https://localhost:5000"
echo ""
echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "1. Deploy OAuth-enabled Flask application"
echo "2. Remove public access from Cloud Run"
echo "3. Test authentication flow"
echo ""

print_success "Google OAuth 2.0 credentials configured successfully!"