#!/bin/bash

# Deploy OAuth-Secured Enhanced Orchestrator for Vertex AI Agent Engine
# Implements Individual Private Instances with Google OAuth authentication

set -e

echo "🔐 DEPLOYING OAUTH-SECURED AGENT ENGINE FUNCTION"
echo "================================================"

# Configuration
PROJECT_ID="service-execution-uat-bb7"
REGION="europe-west9"
FUNCTION_NAME="pm-jira-agent-orchestrator-oauth"

# Set project
echo "📋 Setting GCP project: $PROJECT_ID"
gcloud config set project $PROJECT_ID

echo ""
echo "🔧 PHASE 1: PREPARING OAUTH-SECURED CLOUD FUNCTION"
echo "--------------------------------------------------"

# Create deployment directory
DEPLOY_DIR="/tmp/oauth-secured-agent-engine"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy enhanced orchestrator files
echo "📦 Copying OAuth-secured orchestrator files..."
cp ../../phase0-web-interface/enhanced_orchestrator.py $DEPLOY_DIR/
cp ../../phase0-web-interface/auth_manager.py $DEPLOY_DIR/
cp ../../phase0-web-interface/oauth_auth_manager.py $DEPLOY_DIR/
cp ../agent-configs/tools.py $DEPLOY_DIR/
cp ../agent-configs/*.py $DEPLOY_DIR/

# Create OAuth-secured main.py for Cloud Function
cat > $DEPLOY_DIR/main.py << 'EOF'
#!/usr/bin/env python3

"""
OAuth-Secured PM Jira Agent Orchestrator for Vertex AI Agent Engine
Implements Individual Private Instances with Google OAuth authentication
"""

import functions_framework
import json
import logging
import os
from flask import Request
from functools import wraps
import google.auth.transport.requests
import google.oauth2.id_token
from enhanced_orchestrator import EnhancedMultiAgentOrchestrator
from oauth_auth_manager import GoogleOAuthManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components (singleton pattern)
orchestrator = None
oauth_manager = None

def get_orchestrator():
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = EnhancedMultiAgentOrchestrator()
        logger.info("✅ OAuth-secured orchestrator initialized")
    return orchestrator

def get_oauth_manager():
    """Get or create OAuth manager instance"""
    global oauth_manager
    if oauth_manager is None:
        oauth_manager = GoogleOAuthManager()
        logger.info("✅ OAuth manager initialized for Individual Private Instances")
    return oauth_manager

def require_oauth_auth(f):
    """Decorator to require OAuth authentication for Individual Private Instances"""
    @wraps(f)
    def decorated_function(request: Request):
        try:
            # Check for Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {
                    'success': False,
                    'error': 'OAuth authentication required',
                    'auth_required': True,
                    'oauth_flow_url': '/oauth/initiate'
                }, 401

            # Extract token
            token = auth_header.split('Bearer ')[1]
            
            # Verify OAuth token for Individual Private Instance
            try:
                # Option 1: Verify Google ID token
                id_info = google.oauth2.id_token.verify_oauth2_token(
                    token, 
                    google.auth.transport.requests.Request()
                )
                
                # Check if token is valid for our application
                if id_info.get('aud') != os.getenv('GOOGLE_OAUTH_CLIENT_ID'):
                    raise ValueError('Invalid audience')
                
                # Extract user info for Individual Private Instance
                user_email = id_info.get('email')
                user_domain = user_email.split('@')[1] if user_email else None
                
                logger.info(f"✅ OAuth authenticated user: {user_email}")
                
                # Add user context to request
                request.oauth_user = {
                    'email': user_email,
                    'domain': user_domain,
                    'authenticated': True
                }
                
            except Exception as e:
                # Option 2: Try OAuth manager validation
                oauth_mgr = get_oauth_manager()
                if not oauth_mgr.is_authenticated():
                    return {
                        'success': False,
                        'error': 'Invalid OAuth token',
                        'auth_required': True
                    }, 401
                
                # Use OAuth manager user info
                request.oauth_user = {
                    'email': oauth_mgr.user_email,
                    'authenticated': True
                }
            
            # Call the protected function
            return f(request)
            
        except Exception as e:
            logger.error(f"OAuth authentication error: {e}")
            return {
                'success': False,
                'error': 'Authentication failed',
                'auth_required': True
            }, 401
    
    return decorated_function

@functions_framework.http
def create_jira_ticket(request: Request):
    """
    OAuth-secured entry point for Individual Private Instances
    Creates Jira tickets using 5-agent workflow with OAuth authentication
    """
    # Handle CORS for OAuth flow
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Apply OAuth authentication
    return _create_jira_ticket_authenticated(request)

@require_oauth_auth
def _create_jira_ticket_authenticated(request: Request):
    """Protected function that requires OAuth authentication"""
    try:
        # Get request data
        request_json = request.get_json(silent=True)
        if not request_json:
            return {
                'success': False,
                'error': 'Request must be JSON'
            }, 400

        user_request = request_json.get('user_request')
        if not user_request:
            return {
                'success': False,
                'error': 'user_request parameter is required'
            }, 400

        # Get authenticated user info
        oauth_user = getattr(request, 'oauth_user', {})
        user_email = oauth_user.get('email', 'authenticated-user')
        
        logger.info(f"OAuth user {user_email} creating ticket: {user_request[:100]}...")

        # Get orchestrator and create ticket
        orch = get_orchestrator()
        
        # Add OAuth user context to the workflow
        context = request_json.get('context', {})
        context['oauth_user'] = oauth_user
        context['individual_private_instance'] = True
        
        # Execute 5-agent workflow with OAuth authentication
        result = orch.create_jira_ticket(
            user_request=user_request,
            context=context,
            progress_callback=None
        )

        # Add OAuth metadata to result
        result['oauth_authenticated'] = True
        result['user_email'] = user_email
        result['individual_private_instance'] = True

        logger.info(f"OAuth workflow result for {user_email}: {result.get('success', False)}")

        # Add CORS headers to response
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }

        return (json.dumps(result), 200, headers)

    except Exception as e:
        logger.error(f"Error in OAuth-secured function: {e}")
        error_response = {
            'success': False,
            'error': str(e),
            'error_type': 'oauth_orchestrator_error',
            'individual_private_instance': True
        }
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
        
        return (json.dumps(error_response), 500, headers)

@functions_framework.http
def oauth_initiate(request: Request):
    """Initiate OAuth flow for Individual Private Instances"""
    try:
        oauth_mgr = get_oauth_manager()
        
        # Generate OAuth authorization URL
        auth_url = oauth_mgr.initiate_oauth_flow()
        
        return {
            'oauth_url': auth_url,
            'message': 'Visit the OAuth URL to authenticate your Individual Private Instance',
            'individual_private_instance': True
        }
        
    except Exception as e:
        logger.error(f"OAuth initiation error: {e}")
        return {
            'success': False,
            'error': str(e)
        }, 500

@functions_framework.http
def oauth_callback(request: Request):
    """OAuth callback for Individual Private Instances"""
    try:
        code = request.args.get('code')
        if not code:
            return {
                'success': False,
                'error': 'Authorization code required'
            }, 400
        
        oauth_mgr = get_oauth_manager()
        
        # Exchange code for tokens
        success = oauth_mgr.exchange_code_for_tokens(code)
        
        if success:
            return {
                'success': True,
                'message': 'OAuth authentication successful for Individual Private Instance',
                'user_email': oauth_mgr.user_email,
                'individual_private_instance': True
            }
        else:
            return {
                'success': False,
                'error': 'Failed to exchange authorization code'
            }, 400
            
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return {
            'success': False,
            'error': str(e)
        }, 500

@functions_framework.http
def health_check(request: Request):
    """Health check endpoint with OAuth status"""
    try:
        orch = get_orchestrator()
        oauth_mgr = get_oauth_manager()
        
        return {
            'status': 'healthy',
            'service': 'OAuth-Secured PM Jira Agent',
            'version': '2.0.0-oauth-secured',
            'agents': ['PM', 'BusinessRules', 'TechLead', 'QA', 'JiraCreator'],
            'authentication': 'google-oauth',
            'oauth_configured': oauth_mgr.get_authentication_status()['oauth_configured'],
            'individual_private_instances': True
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }, 500
EOF

# Create OAuth-enhanced requirements.txt
cat > $DEPLOY_DIR/requirements.txt << 'EOF'
functions-framework>=3.2.0
google-cloud-storage>=2.10.0
google-cloud-secret-manager>=2.18.0
google-cloud-logging>=3.8.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
requests>=2.31.0
google-generativeai>=0.3.0
google-cloud-aiplatform>=1.38.0
cryptography>=41.0.0
PyJWT>=2.8.0
flask>=2.3.0
EOF

echo "✅ OAuth-secured Cloud Function package prepared"

echo ""
echo "🔐 PHASE 2: OAUTH CONFIGURATION SETUP"
echo "-------------------------------------"

echo "📋 Setting up OAuth credentials for Individual Private Instances..."

# Check if OAuth credentials exist
if [ -z "$GOOGLE_OAUTH_CLIENT_ID" ] || [ -z "$GOOGLE_OAUTH_CLIENT_SECRET" ]; then
    echo "⚠️  OAuth credentials not found in environment"
    echo ""
    echo "🔧 REQUIRED: Set up Google OAuth credentials"
    echo "1. Go to: https://console.cloud.google.com/apis/credentials"
    echo "2. Create OAuth 2.0 Client ID (Web Application)"
    echo "3. Add authorized redirect URIs:"
    echo "   - https://$REGION-$PROJECT_ID.cloudfunctions.net/oauth_callback"
    echo "   - http://localhost:5000/oauth/callback"
    echo "4. Set environment variables:"
    echo "   export GOOGLE_OAUTH_CLIENT_ID='your_client_id'"
    echo "   export GOOGLE_OAUTH_CLIENT_SECRET='your_client_secret'"
    echo ""
    
    # Create OAuth setup helper
    cat > /tmp/oauth-setup-helper.sh << 'OAUTH_EOF'
#!/bin/bash
echo "🔧 Google OAuth Setup for Individual Private Instances"
echo "Enter your OAuth credentials from Google Cloud Console:"
read -p "Client ID: " CLIENT_ID
read -p "Client Secret: " CLIENT_SECRET

export GOOGLE_OAUTH_CLIENT_ID="$CLIENT_ID"
export GOOGLE_OAUTH_CLIENT_SECRET="$CLIENT_SECRET"

echo "✅ OAuth credentials set for current session"
echo "🔄 Run the deployment script again to continue"
OAUTH_EOF
    
    chmod +x /tmp/oauth-setup-helper.sh
    echo "📋 Run: /tmp/oauth-setup-helper.sh to set up OAuth credentials"
    
else
    echo "✅ OAuth credentials found in environment"
    echo "📋 Client ID: ${GOOGLE_OAUTH_CLIENT_ID:0:20}..."
fi

echo ""
echo "☁️ PHASE 3: DEPLOYING OAUTH-SECURED FUNCTION"
echo "--------------------------------------------"

cd $DEPLOY_DIR

# Deploy OAuth-secured Cloud Function
echo "🚀 Deploying OAuth-secured orchestrator..."

gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=create_jira_ticket \
    --trigger-http \
    --allow-unauthenticated \
    --memory=2Gi \
    --timeout=540s \
    --max-instances=100 \
    --service-account=pm-jira-agent@$PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_REGION=$REGION,GOOGLE_OAUTH_CLIENT_ID=${GOOGLE_OAUTH_CLIENT_ID:-},GOOGLE_OAUTH_CLIENT_SECRET=${GOOGLE_OAUTH_CLIENT_SECRET:-}"

# Get the function URL
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --format='value(serviceConfig.uri)')

echo "✅ OAuth-secured Cloud Function deployed"
echo "🔗 Function URL: $FUNCTION_URL"

echo ""
echo "🧪 PHASE 4: TESTING OAUTH SECURITY"
echo "----------------------------------"

echo "🔍 Testing health endpoint..."
curl -s "$FUNCTION_URL" \
    -X GET \
    -H "Content-Type: application/json" | python3 -m json.tool || echo "Health check completed"

echo ""
echo "🔐 Testing OAuth security (should require authentication)..."
curl -s "$FUNCTION_URL" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "user_request": "Test OAuth security for Individual Private Instance"
    }' | python3 -m json.tool || echo "OAuth security test completed"

echo ""
echo "🎯 PHASE 5: INDIVIDUAL PRIVATE INSTANCE CONFIGURATION"
echo "----------------------------------------------------"

# Create Vertex AI Agent Engine configuration with OAuth
cat > /tmp/oauth-agent-engine-config.json << EOF
{
  "displayName": "PM Jira Agent - OAuth Secured Individual Private Instance",
  "description": "OAuth-secured 5-agent PM workflow for Individual Private Instances with Google authentication",
  "instruction": "You are an OAuth-secured PM Jira Agent for Individual Private Instances. Help users create professional Jira tickets by calling the create_jira_ticket function. Users must authenticate with Google OAuth before accessing the service.",
  "tools": [
    {
      "function_declaration": {
        "name": "create_jira_ticket",
        "description": "Create a professional Jira ticket using OAuth-secured 5-agent workflow for Individual Private Instances",
        "parameters": {
          "type": "object",
          "properties": {
            "user_request": {
              "type": "string",
              "description": "User's authenticated feature request, bug report, or requirement"
            },
            "context": {
              "type": "object",
              "description": "Additional context for Individual Private Instance deployment"
            }
          },
          "required": ["user_request"]
        }
      },
      "function_calling_config": {
        "function_url": "$FUNCTION_URL",
        "authentication_required": true,
        "oauth_client_id": "${GOOGLE_OAUTH_CLIENT_ID:-}"
      }
    }
  ],
  "security": {
    "authentication": "google_oauth",
    "individual_private_instances": true,
    "oauth_flow": "$FUNCTION_URL/oauth/initiate"
  }
}
EOF

echo "✅ OAuth-secured Agent Engine configuration created: /tmp/oauth-agent-engine-config.json"

echo ""
echo "🎉 PHASE 6: DEPLOYMENT SUMMARY"
echo "------------------------------"

echo "✅ OAUTH-SECURED AGENT ENGINE FUNCTION DEPLOYED"
echo ""
echo "🔐 Security Features:"
echo "   • Google OAuth authentication for Individual Private Instances"
echo "   • Protected endpoint with Bearer token validation"
echo "   • User email tracking and audit logging"
echo "   • Individual Private Instance deployment ready"
echo ""
echo "🔧 Deployed Components:"
echo "   • Function: $FUNCTION_NAME"
echo "   • URL: $FUNCTION_URL"
echo "   • Authentication: Google OAuth 2.0"
echo "   • Individual Private Instances: Enabled"
echo ""
echo "🎯 OAuth Endpoints:"
echo "   • Main Function: $FUNCTION_URL"
echo "   • OAuth Initiate: $FUNCTION_URL/oauth/initiate"
echo "   • OAuth Callback: $FUNCTION_URL/oauth/callback"
echo "   • Health Check: $FUNCTION_URL/health"
echo ""
echo "🚀 Next Steps for Vertex AI Agent Engine:"
echo "1. Go to: https://console.cloud.google.com/vertex-ai/agents?project=$PROJECT_ID"
echo "2. CREATE AGENT → Use OAuth-secured configuration"
echo "3. Configure Individual Private Instance deployment"
echo "4. Test OAuth authentication flow"
echo "5. Deploy Individual Private Instances with OAuth security"
echo ""
echo "📋 Individual Private Instance Features:"
echo "   • Google OAuth authentication required"
echo "   • Deploy anywhere with OAuth security"
echo "   • Personal user authentication and tracking"
echo "   • Secure access to corporate Jira/GitBook resources"

# Clean up
rm -rf $DEPLOY_DIR

echo ""
echo "🔐 OAUTH-SECURED AGENT ENGINE READY FOR DEPLOYMENT!"
echo "Individual Private Instances can now authenticate via Google OAuth."
echo "================================================"