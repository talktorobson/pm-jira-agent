#!/bin/bash

# PM Jira Agent Phase 0 - Cloud Deployment Script
# Supports Heroku, Railway, Google Cloud Run, and DigitalOcean

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ERROR="❌"
CLOUD="☁️"

echo -e "${BLUE}${CLOUD} PM Jira Agent Phase 0 - Cloud Deployment${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

# Function to print section headers
print_section() {
    echo -e "\n${PURPLE}$1${NC}"
    echo -e "${PURPLE}$(printf '=%.0s' $(seq 1 ${#1}))${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}${WARNING} $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}${ERROR} $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Deployment function definitions
deploy_heroku() {
    print_section "Deploying to Heroku"
    
    if ! command_exists heroku; then
        print_error "Heroku CLI is not installed."
        echo -e "${CYAN}Install from: https://devcenter.heroku.com/articles/heroku-cli${NC}"
        exit 1
    fi
    
    # Check if logged in
    if ! heroku auth:whoami >/dev/null 2>&1; then
        echo -e "${CYAN}Please log in to Heroku:${NC}"
        heroku login
    fi
    
    # Get app name
    read -p "Enter Heroku app name (leave blank for auto-generated): " APP_NAME
    
    if [ -z "$APP_NAME" ]; then
        APP_NAME="pm-jira-agent-$(whoami)-$(date +%s)"
    fi
    
    echo -e "${CYAN}Creating Heroku app: $APP_NAME${NC}"
    
    # Create app
    heroku create "$APP_NAME" --region us
    
    # Set environment variables
    echo -e "${CYAN}Setting environment variables...${NC}"
    
    if [ -f .env ]; then
        # Read variables from .env file
        while IFS='=' read -r key value; do
            if [[ ! "$key" =~ ^#.* ]] && [ -n "$key" ] && [ -n "$value" ]; then
                heroku config:set "$key=$value" --app "$APP_NAME"
            fi
        done < .env
    fi
    
    # Additional Heroku-specific config
    heroku config:set FLASK_ENV=production --app "$APP_NAME"
    heroku config:set PORT=5000 --app "$APP_NAME"
    
    # Create Procfile for Heroku
    cat > Procfile << 'EOF'
web: gunicorn --bind 0.0.0.0:$PORT app:app --worker-class eventlet -w 1 --timeout 120
EOF
    
    # Deploy
    echo -e "${CYAN}Deploying to Heroku...${NC}"
    git add .
    git commit -m "Deploy PM Jira Agent Phase 0 to Heroku" || true
    git push heroku main || git push heroku master
    
    # Open app
    heroku open --app "$APP_NAME"
    
    print_success "Deployed to Heroku successfully!"
    echo -e "${CYAN}App URL: https://$APP_NAME.herokuapp.com${NC}"
}

deploy_railway() {
    print_section "Deploying to Railway"
    
    if ! command_exists railway; then
        print_error "Railway CLI is not installed."
        echo -e "${CYAN}Install from: https://docs.railway.app/cli/installation${NC}"
        exit 1
    fi
    
    # Login to Railway
    echo -e "${CYAN}Logging in to Railway...${NC}"
    railway login
    
    # Create new project
    echo -e "${CYAN}Creating Railway project...${NC}"
    railway new
    
    # Set environment variables
    echo -e "${CYAN}Setting environment variables...${NC}"
    
    if [ -f .env ]; then
        while IFS='=' read -r key value; do
            if [[ ! "$key" =~ ^#.* ]] && [ -n "$key" ] && [ -n "$value" ]; then
                railway variables set "$key=$value"
            fi
        done < .env
    fi
    
    # Deploy
    echo -e "${CYAN}Deploying to Railway...${NC}"
    railway up
    
    # Get the URL
    URL=$(railway status --json | jq -r '.deployments[0].url' 2>/dev/null || echo "Check Railway dashboard for URL")
    
    print_success "Deployed to Railway successfully!"
    echo -e "${CYAN}App URL: $URL${NC}"
}

deploy_google_cloud_run() {
    print_section "Deploying to Google Cloud Run"
    
    if ! command_exists gcloud; then
        print_error "Google Cloud CLI is not installed."
        echo -e "${CYAN}Install from: https://cloud.google.com/sdk/docs/install${NC}"
        exit 1
    fi
    
    # Get project ID
    read -p "Enter Google Cloud Project ID: " PROJECT_ID
    
    if [ -z "$PROJECT_ID" ]; then
        print_error "Project ID is required for Cloud Run deployment"
        exit 1
    fi
    
    # Set project
    gcloud config set project "$PROJECT_ID"
    
    # Enable required APIs
    echo -e "${CYAN}Enabling required APIs...${NC}"
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable artifactregistry.googleapis.com
    
    # Create Artifact Registry repository
    echo -e "${CYAN}Setting up Artifact Registry...${NC}"
    REGION="us-central1"
    REPO_NAME="pm-jira-agent"
    
    # Create repository if it doesn't exist
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="PM Jira Agent container images" 2>/dev/null || echo "Repository already exists"
    
    # Configure Docker authentication
    gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
    
    # Build and deploy
    echo -e "${CYAN}Building and deploying to Cloud Run...${NC}"
    
    SERVICE_NAME="pm-jira-agent"
    IMAGE_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME"
    
    gcloud builds submit --tag "$IMAGE_URL"
    
    gcloud run deploy "$SERVICE_NAME" \
        --image "$IMAGE_URL" \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --port 5000 \
        --memory 512Mi \
        --timeout 300 \
        --max-instances 10
    
    # Set environment variables
    if [ -f .env ]; then
        ENV_VARS=""
        while IFS='=' read -r key value; do
            if [[ ! "$key" =~ ^#.* ]] && [ -n "$key" ] && [ -n "$value" ]; then
                ENV_VARS="$ENV_VARS,--set-env-vars $key=$value"
            fi
        done < .env
        
        if [ -n "$ENV_VARS" ]; then
            gcloud run services update "$SERVICE_NAME" \
                --region "$REGION" \
                ${ENV_VARS:1}  # Remove leading comma
        fi
    fi
    
    # Get service URL
    URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format="value(status.url)")
    
    print_success "Deployed to Google Cloud Run successfully!"
    echo -e "${CYAN}App URL: $URL${NC}"
}

deploy_digitalocean() {
    print_section "Deploying to DigitalOcean App Platform"
    
    echo -e "${CYAN}Creating DigitalOcean App Spec...${NC}"
    
    # Create app spec for DigitalOcean
    cat > .do/app.yaml << 'EOF'
name: pm-jira-agent
services:
- name: web
  source_dir: /
  github:
    repo: your-username/pm-jira-agent
    branch: main
  run_command: python app.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
  health_check:
    http_path: /health
  envs:
  - key: FLASK_ENV
    value: production
  - key: PORT
    value: "5000"
EOF
    
    print_success "Created DigitalOcean app specification"
    echo -e "${CYAN}Please follow these steps:${NC}"
    echo "1. Go to https://cloud.digitalocean.com/apps"
    echo "2. Click 'Create App'"
    echo "3. Connect your GitHub repository"
    echo "4. Upload the .do/app.yaml file"
    echo "5. Add your environment variables in the DigitalOcean dashboard"
    echo "6. Deploy!"
}

manual_docker_deployment() {
    print_section "Manual Docker Deployment Instructions"
    
    echo -e "${CYAN}To deploy manually on any server with Docker:${NC}"
    echo ""
    echo "1. Copy your project files to the server:"
    echo "   scp -r . user@your-server:/path/to/pm-jira-agent/"
    echo ""
    echo "2. SSH into your server:"
    echo "   ssh user@your-server"
    echo ""
    echo "3. Navigate to the project directory:"
    echo "   cd /path/to/pm-jira-agent/phase0-web-interface"
    echo ""
    echo "4. Edit the .env file with your credentials:"
    echo "   nano .env"
    echo ""
    echo "5. Build and run with Docker Compose:"
    echo "   docker-compose up -d"
    echo ""
    echo "6. (Optional) Set up reverse proxy with Nginx:"
    echo "   # Add Nginx configuration to proxy port 80/443 to port 5000"
    echo ""
    echo "7. (Optional) Set up SSL with Let's Encrypt:"
    echo "   certbot --nginx -d your-domain.com"
    echo ""
    
    # Create nginx config template
    cat > nginx.conf.template << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
    
    print_success "Created nginx.conf.template for reverse proxy setup"
}

# Main deployment menu
print_section "Cloud Deployment Options"

echo "Choose your deployment platform:"
echo "1) Heroku (Free tier available)"
echo "2) Railway (Simple deployment)" 
echo "3) Google Cloud Run (Serverless)"
echo "4) DigitalOcean App Platform"
echo "5) Manual Docker deployment"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        deploy_heroku
        ;;
    2)  
        deploy_railway
        ;;
    3)
        deploy_google_cloud_run
        ;;
    4)
        deploy_digitalocean
        ;;
    5)
        manual_docker_deployment
        ;;
    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

# Final instructions
print_section "Post-Deployment Checklist"

echo -e "${YELLOW}After deployment, please:${NC}"
echo "1. ${CHECK} Test the health endpoint: /health"
echo "2. ${CHECK} Access the configuration page: /config"
echo "3. ${CHECK} Update your JIRA and API credentials"
echo "4. ${CHECK} Test ticket creation with a simple request"
echo "5. ${CHECK} Monitor logs for any errors"
echo ""
echo -e "${GREEN}${ROCKET} Your PM Jira Agent is now deployed to the cloud!${NC}"