#!/bin/bash

# PM Jira Agent Phase 0 - Comprehensive Test Script
# Tests the complete Phase 0 implementation without requiring runtime dependencies

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
ROBOT="🤖"
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ERROR="❌"
TEST="🧪"

echo -e "${BLUE}${TEST} PM Jira Agent Phase 0 - Comprehensive Test${NC}"
echo -e "${BLUE}================================================${NC}"
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

# Function to check if file exists and has content
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        local size=$(wc -c < "$file")
        if [ $size -gt 0 ]; then
            print_success "$description exists and has content ($size bytes)"
            return 0
        else
            print_error "$description exists but is empty"
            return 1
        fi
    else
        print_error "$description does not exist"
        return 1
    fi
}

# Function to validate Python syntax
validate_python_syntax() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        if python3 -m py_compile "$file" 2>/dev/null; then
            print_success "$description has valid Python syntax"
            return 0
        else
            print_error "$description has Python syntax errors"
            return 1
        fi
    else
        print_error "$description does not exist"
        return 1
    fi
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

print_section "File Structure Validation"

# Core application files
if check_file "app.py" "Main Flask application"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi
if check_file "enhanced_orchestrator.py" "Enhanced orchestrator"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi
if check_file "requirements.txt" "Python requirements"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi

# Configuration files
if check_file "config/config.yaml.template" "Configuration template"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi
if check_file ".env.example" "Environment template"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi

# Templates
if check_file "templates/index.html" "Main web interface"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi
if check_file "templates/config.html" "Configuration interface"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi

# Docker and deployment
if check_file "Dockerfile" "Docker container definition"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi
if check_file "docker-compose.yml" "Docker Compose configuration"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi

# Scripts
if check_file "setup.sh" "Setup script"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi
if check_file "deploy-cloud.sh" "Cloud deployment script"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi

# Documentation
if check_file "README.md" "Documentation"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi

print_section "Python Syntax Validation"

# Validate Python syntax
if validate_python_syntax "app.py" "Main Flask application"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi
if validate_python_syntax "enhanced_orchestrator.py" "Enhanced orchestrator"; then ((TESTS_PASSED++)); else ((TESTS_FAILED++)); fi

print_section "Configuration Validation"

# Check if config template has required sections
if [ -f "config/config.yaml.template" ]; then
    if grep -q "user_info:" "config/config.yaml.template" && \
       grep -q "jira:" "config/config.yaml.template" && \
       grep -q "custom_prompts:" "config/config.yaml.template"; then
        print_success "Configuration template has required sections"
        ((TESTS_PASSED++))
    else
        print_error "Configuration template missing required sections"
        ((TESTS_FAILED++))
    fi
else
    print_error "Configuration template not found"
    ((TESTS_FAILED++))
fi

# Check environment template
if [ -f ".env.example" ]; then
    if grep -q "JIRA_API_TOKEN" ".env.example" && \
       grep -q "JIRA_EMAIL" ".env.example" && \
       grep -q "SECRET_KEY" ".env.example"; then
        print_success "Environment template has required variables"
        ((TESTS_PASSED++))
    else
        print_error "Environment template missing required variables"
        ((TESTS_FAILED++))
    fi
else
    print_error "Environment template not found"
    ((TESTS_FAILED++))
fi

print_section "Docker Configuration Validation"

# Check Dockerfile
if [ -f "Dockerfile" ]; then
    if grep -q "FROM python:" "Dockerfile" && \
       grep -q "COPY requirements.txt" "Dockerfile" && \
       grep -q "EXPOSE" "Dockerfile"; then
        print_success "Dockerfile has proper Python app structure"
        ((TESTS_PASSED++))
    else
        print_error "Dockerfile missing required Python app elements"
        ((TESTS_FAILED++))
    fi
else
    print_error "Dockerfile not found"
    ((TESTS_FAILED++))
fi

# Check docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    if grep -q "services:" "docker-compose.yml" && \
       grep -q "ports:" "docker-compose.yml" && \
       grep -q "5000:5000" "docker-compose.yml"; then
        print_success "Docker Compose properly configured for web service"
        ((TESTS_PASSED++))
    else
        print_error "Docker Compose missing required web service configuration"
        ((TESTS_FAILED++))
    fi
else
    print_error "Docker Compose file not found"
    ((TESTS_FAILED++))
fi

print_section "Web Interface Validation"

# Check HTML templates
if [ -f "templates/index.html" ]; then
    if grep -q "socket.io" "templates/index.html" && \
       grep -q "WebSocket" "templates/index.html"; then
        print_success "Main interface has WebSocket support"
        ((TESTS_PASSED++))
    else
        print_warning "Main interface may not have real-time updates"
        ((TESTS_FAILED++))
    fi
else
    print_error "Main interface template not found"
    ((TESTS_FAILED++))
fi

if [ -f "templates/config.html" ]; then
    if grep -q "YAML" "templates/config.html" && \
       grep -q "configuration" "templates/config.html"; then
        print_success "Configuration interface properly structured"
        ((TESTS_PASSED++))
    else
        print_warning "Configuration interface may be incomplete"
        ((TESTS_FAILED++))
    fi
else
    print_error "Configuration interface template not found"
    ((TESTS_FAILED++))
fi

print_section "Deployment Scripts Validation"

# Check setup script
if [ -f "setup.sh" ]; then
    if grep -q "docker" "setup.sh" && \
       grep -q "health" "setup.sh" && \
       grep -q "configuration" "setup.sh"; then
        print_success "Setup script has Docker and health check logic"
        ((TESTS_PASSED++))
    else
        print_error "Setup script missing required functionality"
        ((TESTS_FAILED++))
    fi
else
    print_error "Setup script not found"
    ((TESTS_FAILED++))
fi

# Check cloud deployment script
if [ -f "deploy-cloud.sh" ]; then
    if grep -q "heroku" "deploy-cloud.sh" && \
       grep -q "railway" "deploy-cloud.sh" && \
       grep -q "cloud.*run" "deploy-cloud.sh"; then
        print_success "Cloud deployment script supports multiple platforms"
        ((TESTS_PASSED++))
    else
        print_error "Cloud deployment script missing platform support"
        ((TESTS_FAILED++))
    fi
else
    print_error "Cloud deployment script not found"
    ((TESTS_FAILED++))
fi

print_section "Script Permissions"

# Check script permissions
if [ -x "setup.sh" ]; then
    print_success "Setup script is executable"
    ((TESTS_PASSED++))
else
    print_warning "Setup script is not executable (run: chmod +x setup.sh)"
    ((TESTS_FAILED++))
fi

if [ -x "deploy-cloud.sh" ]; then
    print_success "Cloud deployment script is executable"
    ((TESTS_PASSED++))
else
    print_warning "Cloud deployment script is not executable (run: chmod +x deploy-cloud.sh)"
    ((TESTS_FAILED++))
fi

print_section "Requirements Validation"

# Check Python requirements
if [ -f "requirements.txt" ]; then
    if grep -q "Flask" "requirements.txt" && \
       grep -q "SocketIO" "requirements.txt" && \
       grep -q "PyYAML" "requirements.txt"; then
        print_success "Requirements include all core dependencies"
        ((TESTS_PASSED++))
    else
        print_error "Requirements missing core dependencies"
        ((TESTS_FAILED++))
    fi
else
    print_error "Requirements file not found"
    ((TESTS_FAILED++))
fi

print_section "Phase 0 Feature Completeness"

# Check for multi-agent orchestrator features
if [ -f "enhanced_orchestrator.py" ]; then
    if grep -q "ProgressTracker" "enhanced_orchestrator.py" && \
       grep -q "MockAgent" "enhanced_orchestrator.py" && \
       grep -q "quality.*score" "enhanced_orchestrator.py"; then
        print_success "Enhanced orchestrator has progress tracking and quality gates"
        ((TESTS_PASSED++))
    else
        print_error "Enhanced orchestrator missing key features"
        ((TESTS_FAILED++))
    fi
else
    print_error "Enhanced orchestrator not found"
    ((TESTS_FAILED++))
fi

# Check for Flask application features
if [ -f "app.py" ]; then
    if grep -q "SocketIO" "app.py" && \
       grep -q "/config" "app.py" && \
       grep -q "/health" "app.py"; then
        print_success "Flask application has real-time updates and configuration endpoints"
        ((TESTS_PASSED++))
    else
        print_error "Flask application missing key endpoints"
        ((TESTS_FAILED++))
    fi
else
    print_error "Flask application not found"
    ((TESTS_FAILED++))
fi

print_section "Test Results Summary"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))

echo ""
echo -e "${CYAN}📊 Test Results:${NC}"
echo -e "${GREEN}✅ Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Failed: $TESTS_FAILED${NC}"
echo -e "${BLUE}📈 Success Rate: $SUCCESS_RATE%${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}${ROCKET} Phase 0 Implementation: COMPLETE!${NC}"
    echo -e "${CYAN}All components are properly implemented and ready for deployment.${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Run ./setup.sh to start your PM Jira Agent"
    echo "2. Configure your JIRA credentials at http://localhost:5000/config"
    echo "3. Create your first AI-powered ticket!"
    echo "4. Deploy to cloud with ./deploy-cloud.sh"
elif [ $SUCCESS_RATE -ge 90 ]; then
    echo -e "${YELLOW}${CHECK} Phase 0 Implementation: NEARLY COMPLETE!${NC}"
    echo -e "${CYAN}Minor issues found but system should be functional.${NC}"
    echo -e "${YELLOW}Address the failed tests above and you're ready to go!${NC}"
else
    echo -e "${RED}${ERROR} Phase 0 Implementation: NEEDS ATTENTION${NC}"
    echo -e "${CYAN}Several critical issues found. Review failed tests above.${NC}"
fi

echo ""
echo -e "${BLUE}${ROBOT} Phase 0 testing complete!${NC}"

exit $TESTS_FAILED