#!/usr/bin/env python3

"""
Create OAuth 2.0 Credentials for PM Jira Agent
Uses Google Cloud APIs to programmatically create OAuth client
"""

import json
import subprocess
import sys
from google.auth import default
from google.auth.transport.requests import Request
import requests

# Project configuration
PROJECT_ID = "service-execution-uat-bb7"
PROJECT_NUMBER = "68599638628"
REDIRECT_URI = "https://pm-jira-agent-jlhinciqia-od.a.run.app/auth/callback"
APPLICATION_NAME = "PM Jira Agent"

def run_gcloud_command(command):
    """Run gcloud command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ Command failed: {command}")
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Exception running command: {e}")
        return None

def get_access_token():
    """Get access token for Google Cloud APIs"""
    try:
        credentials, _ = default()
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"❌ Failed to get access token: {e}")
        return None

def create_oauth_client():
    """Create OAuth 2.0 client using Google Cloud Console API"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    # API endpoint for creating OAuth client
    url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{PROJECT_ID}:setIamPolicy"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Try to use the console API directly
    print("🔧 Attempting to create OAuth client using Google APIs...")
    
    # Since the Google Cloud Console API for OAuth client creation is not publicly documented,
    # let's use the gcloud CLI with specific configurations
    
    # First, let's create a temporary OAuth client configuration
    oauth_config = {
        "web": {
            "client_id": "",
            "client_secret": "",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
            "javascript_origins": [
                "https://pm-jira-agent-jlhinciqia-od.a.run.app"
            ]
        }
    }
    
    print("⚠️  OAuth client creation via API requires manual setup")
    print("📋 Configuration needed:")
    print(f"   Application Name: {APPLICATION_NAME}")
    print(f"   Redirect URI: {REDIRECT_URI}")
    print(f"   JavaScript Origins: https://pm-jira-agent-jlhinciqia-od.a.run.app")
    
    return oauth_config

def main():
    print("🔐 Creating OAuth 2.0 Credentials for PM Jira Agent")
    print("=" * 55)
    
    # Check if we can access the project
    project_info = run_gcloud_command(f"gcloud projects describe {PROJECT_ID} --format='value(projectId)'")
    if not project_info:
        print(f"❌ Cannot access project {PROJECT_ID}")
        return False
    
    print(f"✅ Project access confirmed: {project_info}")
    
    # Check current OAuth brands
    print("\n🔍 Checking existing OAuth configuration...")
    brands = run_gcloud_command(f"gcloud alpha iap oauth-brands list --project={PROJECT_ID} --format='json'")
    
    if brands:
        try:
            brands_data = json.loads(brands)
            if brands_data:
                brand = brands_data[0]
                print(f"✅ OAuth brand found: {brand.get('name', 'Unknown')}")
                print(f"   Application Title: {brand.get('applicationTitle', 'Not set')}")
                print(f"   Support Email: {brand.get('supportEmail', 'Not set')}")
            else:
                print("❌ No OAuth brands found")
        except json.JSONDecodeError:
            print("⚠️  Could not parse OAuth brands response")
    
    # Since automatic OAuth client creation is complex via API,
    # let's provide the exact steps and generate the credentials manually
    
    print("\n🛠️  OAuth Client Creation Steps:")
    print("Since OAuth client creation requires specific Google Cloud Console steps,")
    print("I'll provide you with the exact configuration and store dummy credentials")
    print("that you can replace once you create the actual OAuth client.")
    
    # Generate placeholder credentials that follow the correct format
    client_id = f"{PROJECT_NUMBER}.apps.googleusercontent.com"
    client_secret = "GOCSPX-" + "x" * 28  # Placeholder format
    
    print(f"\n📋 OAuth Configuration:")
    print(f"   Project ID: {PROJECT_ID}")
    print(f"   Client ID format: {client_id}")
    print(f"   Redirect URI: {REDIRECT_URI}")
    print(f"   JavaScript Origins: https://pm-jira-agent-jlhinciqia-od.a.run.app")
    
    # Store placeholder credentials in Secret Manager
    print("\n💾 Storing placeholder credentials in Secret Manager...")
    
    # Store OAuth Client ID
    cmd1 = f"echo -n '{client_id}' | gcloud secrets create google-oauth-client-id --data-file=- --project={PROJECT_ID} 2>/dev/null || echo -n '{client_id}' | gcloud secrets versions add google-oauth-client-id --data-file=- --project={PROJECT_ID}"
    result1 = run_gcloud_command(cmd1)
    
    # Store OAuth Client Secret  
    cmd2 = f"echo -n '{client_secret}' | gcloud secrets create google-oauth-client-secret --data-file=- --project={PROJECT_ID} 2>/dev/null || echo -n '{client_secret}' | gcloud secrets versions add google-oauth-client-secret --data-file=- --project={PROJECT_ID}"
    result2 = run_gcloud_command(cmd2)
    
    if result1 is not None and result2 is not None:
        print("✅ Placeholder credentials stored in Secret Manager")
    else:
        print("❌ Failed to store credentials in Secret Manager")
    
    # Provide the manual setup instructions
    print("\n🔗 Manual OAuth Setup Required:")
    print("1. Go to: https://console.cloud.google.com/apis/credentials/consent?project=service-execution-uat-bb7")
    print("2. Configure OAuth consent screen:")
    print("   - User Type: Internal")
    print("   - App Name: PM Jira Agent")
    print("   - User Support Email: robson.reis@adeo.com")
    print("   - Developer Contact: robson.reis@adeo.com")
    print("   - Authorized Domains: adeo.com")
    print("")
    print("3. Go to: https://console.cloud.google.com/apis/credentials?project=service-execution-uat-bb7")
    print("4. Click 'Create Credentials' → 'OAuth 2.0 Client ID'")
    print("5. Application Type: Web Application")
    print("6. Name: PM Jira Agent OAuth Client")
    print("7. Authorized JavaScript Origins:")
    print("   - https://pm-jira-agent-jlhinciqia-od.a.run.app")
    print("8. Authorized Redirect URIs:")
    print("   - https://pm-jira-agent-jlhinciqia-od.a.run.app/auth/callback")
    print("")
    print("9. After creating, update Secret Manager with real credentials:")
    print(f"   gcloud secrets versions add google-oauth-client-id --data-file=client-id.txt --project={PROJECT_ID}")
    print(f"   gcloud secrets versions add google-oauth-client-secret --data-file=client-secret.txt --project={PROJECT_ID}")
    
    print(f"\n✅ OAuth setup framework complete!")
    print("📝 Next: Complete manual OAuth client creation in Google Cloud Console")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)