#!/bin/bash

# PM Jira Agent Phase 0 - One-Click Setup Script
# This script sets up your personal PM Jira Agent instance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis for better UX
ROBOT="🤖"
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ERROR="❌"
CONFIG="⚙️"
DOCKER="🐳"

echo -e "${BLUE}${ROBOT} PM Jira Agent Phase 0 Setup${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""
echo -e "${CYAN}Transform your ideas into professional Jira tickets in under 2 minutes!${NC}"
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

# Check prerequisites
print_section "Checking Prerequisites"

if ! command_exists docker; then
    print_error "Docker is required but not installed."
    echo -e "${CYAN}Please install Docker from: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi
print_success "Docker is installed"

if ! command_exists docker-compose; then
    print_warning "docker-compose not found, trying docker compose..."
    if ! docker compose version >/dev/null 2>&1; then
        print_error "Neither docker-compose nor 'docker compose' is available."
        echo -e "${CYAN}Please install Docker Compose from: https://docs.docker.com/compose/install/${NC}"
        exit 1
    else
        DOCKER_COMPOSE_CMD="docker compose"
        print_success "Docker Compose (v2) is available"
    fi
else
    DOCKER_COMPOSE_CMD="docker-compose"
    print_success "Docker Compose (v1) is installed"
fi

# Create directory structure
print_section "Setting Up Directory Structure"

# Create necessary directories
mkdir -p config logs
print_success "Created config and logs directories"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_section "Creating Environment Configuration"
    
    cat > .env << 'EOF'
# PM Jira Agent Environment Configuration
# Edit these values with your actual credentials

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=service-execution-uat-bb7
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json

# JIRA Configuration (REQUIRED)
JIRA_API_TOKEN=your-jira-api-token-here
JIRA_EMAIL=your-email@company.com

# GitBook Configuration (OPTIONAL)
GITBOOK_API_KEY=your-gitbook-api-key-here

# Security
SECRET_KEY=your-secret-key-here
EOF
    
    print_success "Created .env file template"
    print_warning "Please edit .env with your actual API credentials"
else
    print_success ".env file already exists"
fi

# Create default config if it doesn't exist
if [ ! -f config/config.yaml ]; then
    print_section "Creating Default Configuration"
    
    if [ -f config/config.yaml.template ]; then
        cp config/config.yaml.template config/config.yaml
    else
        cat > config/config.yaml << 'EOF'
user_info:
  name: "Product Manager"
  email: "pm@company.com"  
  team: "Product Team"

jira:
  base_url: "https://yourcompany.atlassian.net"
  project_key: "PROJ"
  default_issue_type: "Story"
  default_priority: "Medium"

gitbook:
  enabled: false
  space_id: ""

custom_prompts:
  company_context: "We are a technology company focused on innovative solutions"
  writing_style: "professional"
  stakeholder_mapping:
    Security Team: "security@company.com"
    UX Team: "ux@company.com" 
    Engineering: "dev@company.com"

business_rules:
  ui_ux_guidelines: "Follow modern UI/UX best practices"
  security_requirements: "All user data must be secure"
  performance_standards: "Optimize for fast user experience"
EOF
    fi
    
    print_success "Created default configuration file"
    print_warning "Please edit config/config.yaml with your company details"
else
    print_success "Configuration file already exists"
fi

# Function to prompt for configuration
configure_interactive() {
    print_section "Interactive Configuration"
    
    echo -e "${CYAN}Let's configure your PM Jira Agent instance:${NC}"
    echo ""
    
    # JIRA Configuration
    echo -e "${YELLOW}JIRA Configuration:${NC}"
    read -p "JIRA Base URL (e.g., https://company.atlassian.net): " JIRA_URL
    read -p "JIRA Project Key (e.g., PROJ): " JIRA_PROJECT
    read -p "Your JIRA Email: " JIRA_EMAIL_INPUT
    read -s -p "JIRA API Token (hidden): " JIRA_TOKEN_INPUT
    echo ""
    
    # Company Information
    echo -e "\n${YELLOW}Company Information:${NC}"
    read -p "Your Name: " USER_NAME
    read -p "Your Team: " USER_TEAM
    read -p "Company Description: " COMPANY_CONTEXT
    
    # Update .env file
    if [ -n "$JIRA_EMAIL_INPUT" ]; then
        sed -i.bak "s/JIRA_EMAIL=.*/JIRA_EMAIL=$JIRA_EMAIL_INPUT/" .env
    fi
    if [ -n "$JIRA_TOKEN_INPUT" ]; then
        sed -i.bak "s/JIRA_API_TOKEN=.*/JIRA_API_TOKEN=$JIRA_TOKEN_INPUT/" .env
    fi
    
    # Update config.yaml
    if [ -n "$USER_NAME" ]; then
        sed -i.bak "s/name: \".*\"/name: \"$USER_NAME\"/" config/config.yaml
    fi
    if [ -n "$USER_TEAM" ]; then
        sed -i.bak "s/team: \".*\"/team: \"$USER_TEAM\"/" config/config.yaml
    fi
    if [ -n "$JIRA_URL" ]; then
        sed -i.bak "s|base_url: \".*\"|base_url: \"$JIRA_URL\"|" config/config.yaml
    fi
    if [ -n "$JIRA_PROJECT" ]; then
        sed -i.bak "s/project_key: \".*\"/project_key: \"$JIRA_PROJECT\"/" config/config.yaml
    fi
    if [ -n "$COMPANY_CONTEXT" ]; then
        sed -i.bak "s/company_context: \".*\"/company_context: \"$COMPANY_CONTEXT\"/" config/config.yaml
    fi
    
    # Clean up backup files
    rm -f .env.bak config/config.yaml.bak
    
    print_success "Configuration updated with your information"
}

# Ask if user wants interactive configuration
echo ""
read -p "Would you like to configure your instance interactively? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    configure_interactive
fi

# Build and start the application
print_section "Building and Starting PM Jira Agent"

echo -e "${CYAN}Building Docker container...${NC}"
$DOCKER_COMPOSE_CMD build

echo -e "${CYAN}Starting PM Jira Agent...${NC}"
$DOCKER_COMPOSE_CMD up -d

# Wait for health check
print_section "Waiting for Application to Start"

echo -e "${CYAN}Checking application health...${NC}"
RETRY_COUNT=0
MAX_RETRIES=30

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:5000/health >/dev/null 2>&1; then
        print_success "Application is healthy and ready!"
        break
    else
        echo -n "."
        sleep 2
        ((RETRY_COUNT++))
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "Application failed to start properly"
    echo -e "${CYAN}Check logs with: $DOCKER_COMPOSE_CMD logs${NC}"
    exit 1
fi

# Success message
print_section "Setup Complete!"

echo -e "${GREEN}${ROCKET} Your PM Jira Agent is now running!${NC}"
echo ""
echo -e "${CYAN}🌐 Web Interface: ${NC}${BLUE}http://localhost:5000${NC}"
echo -e "${CYAN}${CONFIG} Configuration: ${NC}${BLUE}http://localhost:5000/config${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Open http://localhost:5000 in your browser"
echo "2. Click 'Settings' to review your configuration"
echo "3. Try creating your first AI-powered Jira ticket!"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "• View logs:        $DOCKER_COMPOSE_CMD logs -f"
echo "• Stop application: $DOCKER_COMPOSE_CMD down"
echo "• Restart:          $DOCKER_COMPOSE_CMD restart"
echo "• Update:           git pull && $DOCKER_COMPOSE_CMD build && $DOCKER_COMPOSE_CMD up -d"
echo ""
echo -e "${GREEN}${CHECK} Setup completed successfully!${NC}"
echo -e "${CYAN}Happy ticket creating! ${ROBOT}${NC}"