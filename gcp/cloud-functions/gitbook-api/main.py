"""
GitBook API Cloud Function
Handles GitBook knowledge retrieval for PM Jira Agent
"""

import json
import requests
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
def gitbook_api(request: Request):
    """
    Cloud Function to interact with GitBook API
    Expected request body:
    {
        "action": "get_content" | "search",
        "query": "optional search query",
        "space_id": "optional space override"
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
        # Get GitBook API key from Secret Manager
        api_key = get_secret("gitbook-api-key").strip()
        space_id = "Jw57BieQciFYoCHgwVlm"  # Default space ID
        
        # Parse request
        request_json = request.get_json(silent=True)
        if not request_json:
            return (json.dumps({"error": "Invalid JSON payload"}), 400, headers)
        
        action = request_json.get("action", "get_content")
        query = request_json.get("query", "")
        custom_space_id = request_json.get("space_id")
        
        if custom_space_id:
            space_id = custom_space_id
        
        # GitBook API headers (Bearer token for personal access tokens)
        api_headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        if action == "get_content":
            # Get space content using personal token endpoints
            url = f"https://api.gitbook.com/v1/spaces/{space_id}"
            response = requests.get(url, headers=api_headers, timeout=30)
            
        elif action == "search":
            # Search within space content (no direct search endpoint, so get content and search)
            url = f"https://api.gitbook.com/v1/spaces/{space_id}/content"
            response = requests.get(url, headers=api_headers, timeout=30)
            
        else:
            return (json.dumps({"error": f"Unknown action: {action}"}), 400, headers)
        
        # Handle GitBook API response
        if response.status_code == 200:
            data = response.json()
            
            if action == "search":
                # For search action, extract pages and search through them
                query_lower = query.lower() if query else ""
                search_results = []
                
                pages = data.get("pages", [])
                for page in pages:
                    title = page.get("title", "")
                    description = page.get("description", "")
                    page_url = page.get("urls", {}).get("app", "")
                    
                    # Simple search: check if query appears in title or description
                    if query_lower and (query_lower in title.lower() or query_lower in description.lower()):
                        search_results.append({
                            "title": title,
                            "snippet": description[:200] + ("..." if len(description) > 200 else ""),
                            "url": page_url,
                            "relevance": 1.0 if query_lower in title.lower() else 0.7
                        })
                
                # If no matches found, return top pages for general context
                if not search_results and pages:
                    search_results = [{
                        "title": page.get("title", ""),
                        "snippet": page.get("description", "")[:200] + ("..." if len(page.get("description", "")) > 200 else ""),
                        "url": page.get("urls", {}).get("app", ""),
                        "relevance": 0.5
                    } for page in pages[:3]]
                
                return (json.dumps({
                    "success": True,
                    "results": search_results,
                    "query": query,
                    "total_pages": len(pages),
                    "action": action,
                    "space_id": space_id
                }), 200, headers)
            
            else:
                # For get_content action, extract content based on GitBook API structure
                content = ""
                if "content" in data:
                    content = data["content"].get("markdown", "") or data["content"].get("text", "") or str(data["content"])
                else:
                    content = data.get("markdown", "") or data.get("text", "") or json.dumps(data)
                
                return (json.dumps({
                    "success": True,
                    "content": content,
                    "raw_data": data,
                    "action": action,
                    "space_id": space_id
                }), 200, headers)
            
        else:
            return (json.dumps({
                "error": f"GitBook API error: {response.status_code}",
                "message": response.text
            }), response.status_code, headers)
            
    except Exception as e:
        return (json.dumps({
            "error": "Internal server error",
            "message": str(e)
        }), 500, headers)