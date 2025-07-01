"""
Jira API Cloud Function
Handles Jira ticket operations for PM Jira Agent
"""

import json
import requests
import base64
from google.cloud import secretmanager
from flask import Request
import functions_framework

def get_secret(secret_id: str) -> str:
    """Retrieve secret from GCP Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/service-execution-uat-bb7/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

@functions_framework.http
def jira_api(request: Request):
    """
    Cloud Function to interact with Jira API
    Expected request body:
    {
        "action": "create_ticket" | "get_tickets" | "get_ticket",
        "ticket_data": {...}, # for create_ticket
        "ticket_id": "...", # for get_ticket
        "jql": "..." # for get_tickets
    }
    """
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }
    
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    try:
        # Get Jira API credentials from Secret Manager
        jira_token = get_secret("jira-api-token").strip()
        
        # Jira configuration
        jira_base_url = "https://jira.adeo.com"
        project_key = "AHSSI"
        
        # Parse request
        request_json = request.get_json(silent=True)
        if not request_json:
            return (json.dumps({"error": "Invalid JSON payload"}), 400, headers)
        
        action = request_json.get("action")
        
        # Jira API headers (using Bearer token for SSO environments)
        api_headers = {
            "Authorization": f"Bearer {jira_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if action == "create_ticket":
            # Create Jira ticket
            ticket_data = request_json.get("ticket_data", {})
            
            # Ensure required fields
            if not ticket_data.get("summary"):
                return (json.dumps({"error": "Missing required field: summary"}), 400, headers)
            
            # Build Jira ticket payload
            jira_payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": ticket_data.get("summary"),
                    "description": ticket_data.get("description", ""),
                    "issuetype": {"name": ticket_data.get("issue_type", "Story")},
                    "priority": {"name": ticket_data.get("priority", "Medium")}
                }
            }
            
            # Add optional fields if provided
            if ticket_data.get("assignee"):
                jira_payload["fields"]["assignee"] = {"emailAddress": ticket_data["assignee"]}
            
            if ticket_data.get("labels"):
                jira_payload["fields"]["labels"] = ticket_data["labels"]
            
            if ticket_data.get("components"):
                jira_payload["fields"]["components"] = [{"name": comp} for comp in ticket_data["components"]]
            
            url = f"{jira_base_url}/rest/api/2/issue"
            response = requests.post(url, headers=api_headers, json=jira_payload, timeout=30)
            
        elif action == "get_tickets":
            # Get tickets using JQL
            jql = request_json.get("jql", f"project = {project_key} ORDER BY created DESC")
            max_results = request_json.get("max_results", 50)
            
            url = f"{jira_base_url}/rest/api/2/search"
            params = {
                "jql": jql,
                "maxResults": max_results,
                "fields": "summary,status,assignee,created,updated,priority,issuetype,description"
            }
            response = requests.get(url, headers=api_headers, params=params, timeout=30)
            
        elif action == "get_ticket":
            # Get specific ticket
            ticket_id = request_json.get("ticket_id")
            if not ticket_id:
                return (json.dumps({"error": "Missing required field: ticket_id"}), 400, headers)
            
            url = f"{jira_base_url}/rest/api/2/issue/{ticket_id}"
            response = requests.get(url, headers=api_headers, timeout=30)
            
        else:
            return (json.dumps({"error": f"Unknown action: {action}"}), 400, headers)
        
        # Handle Jira API response
        if response.status_code in [200, 201]:
            data = response.json()
            return (json.dumps({
                "success": True,
                "data": data,
                "action": action
            }), response.status_code, headers)
            
        else:
            return (json.dumps({
                "error": f"Jira API error: {response.status_code}",
                "message": response.text
            }), response.status_code, headers)
            
    except Exception as e:
        return (json.dumps({
            "error": "Internal server error",
            "message": str(e)
        }), 500, headers)