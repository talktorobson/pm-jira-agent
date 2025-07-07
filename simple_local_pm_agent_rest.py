#!/usr/bin/env python3
"""
Simple Local PM Agent with REST API Access
Uses direct HTTP calls to Vertex AI REST API instead of gRPC
"""

import asyncio
import json
import logging
import httpx
from typing import Dict, Any
from google.auth import default
from google.auth.transport.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleLocalPMAgentREST:
    """
    Local PM Agent with direct REST API access to Vertex AI, GitBook, and Jira
    """
    
    def __init__(self):
        # Vertex AI configuration
        self.project_id = "service-execution-uat-bb7"
        self.location = "europe-west1"
        self.model_id = "gemini-1.5-flash"
        
        # Get Google Cloud credentials
        self.credentials, _ = default()
        
        # API credentials
        self.gitbook_token = "gb_api_20IQSSLBjb4Jxeq9sTnX2wiknnyePfIefDvICnxc"
        self.gitbook_space_id = "Jw57BieQciFYoCHgwVlm"
        
        # Jira credentials (using hardcoded for testing - should use Secret Manager)
        self.jira_base_url = "https://jira.adeo.com"
        self.jira_email = "robson.reis@adeo.com"
        self.jira_token = None  # Will try to load from env or skip
        
        logger.info("✅ Simple Local PM Agent (REST) initialized")
        logger.info(f"🌍 Using project: {self.project_id} in {self.location}")
    
    def _get_access_token(self) -> str:
        """Get Google Cloud access token for API calls"""
        try:
            # Refresh credentials if needed
            if not self.credentials.valid:
                self.credentials.refresh(Request())
            
            return self.credentials.token
            
        except Exception as e:
            logger.error(f"❌ Failed to get access token: {e}")
            raise Exception(f"Authentication failed: {str(e)}")
    
    async def search_gitbook(self, query: str) -> Dict[str, Any]:
        """Search GitBook documentation"""
        try:
            headers = {
                "Authorization": f"Bearer {self.gitbook_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.gitbook.com/v1/spaces/{self.gitbook_space_id}/search",
                    headers=headers,
                    params={"query": query, "limit": 5},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"📚 GitBook search: {len(data.get('items', []))} results for '{query}'")
                    return data
                else:
                    logger.error(f"❌ GitBook API error: {response.status_code}")
                    return {"items": [], "error": f"API returned {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ GitBook search failed: {e}")
            return {"items": [], "error": str(e)}
    
    async def call_vertex_ai_rest(self, prompt: str) -> str:
        """Call Vertex AI Gemini using REST API instead of gRPC"""
        
        try:
            # Get access token
            access_token = self._get_access_token()
            
            # Vertex AI REST API endpoint
            url = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_id}:generateContent"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Request body for Vertex AI REST API
            data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generation_config": {
                    "temperature": 0.3,
                    "max_output_tokens": 2000,
                    "top_p": 0.8,
                    "top_k": 40
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract text from response
                    candidates = result.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                    
                    raise Exception("Invalid response format from Vertex AI")
                    
                else:
                    error_text = response.text
                    logger.error(f"❌ Vertex AI REST API error: {response.status_code} - {error_text}")
                    raise Exception(f"Vertex AI API returned {response.status_code}: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Vertex AI REST API call failed: {e}")
            raise Exception(f"Vertex AI processing failed: {str(e)}")
    
    async def process_with_research(self, user_request: str) -> Dict[str, Any]:
        """Process user request with API research using REST API"""
        
        logger.info(f"🔬 LOCAL PM Agent (REST) processing: {user_request}")
        
        try:
            # Step 1: API Research
            logger.info("📚 Researching GitBook documentation...")
            gitbook_results = await self.search_gitbook(user_request)
            
            # Step 2: Prepare research context for AI
            research_context = self._format_research_context(gitbook_results)
            
            # Step 3: AI Processing with research using REST API
            logger.info("🤖 Processing with Vertex AI Gemini Pro (REST API)...")
            ai_response = await self._call_vertex_ai_with_research(user_request, research_context)
            
            # Step 4: Format as standardized JSON
            standardized_output = self._format_standardized_output(ai_response, gitbook_results)
            
            logger.info("✅ LOCAL PM Agent (REST) completed successfully")
            return standardized_output
            
        except Exception as e:
            logger.error(f"❌ LOCAL PM Agent (REST) failed: {e}")
            raise Exception(f"Local PM Agent processing failed: {str(e)}")
    
    def _format_research_context(self, gitbook_results: Dict) -> str:
        """Format research results for AI context"""
        
        context_parts = []
        
        # GitBook context
        gitbook_items = gitbook_results.get("items", [])
        if gitbook_items:
            context_parts.append("## GitBook Documentation Found:")
            for item in gitbook_items[:3]:  # Top 3 results
                title = item.get("title", "Unknown")
                snippet = item.get("snippet", "")[:200]
                context_parts.append(f"- {title}: {snippet}")
        
        return "\n".join(context_parts) if context_parts else "No relevant documentation found."
    
    async def _call_vertex_ai_with_research(self, user_request: str, research_context: str) -> str:
        """Call Vertex AI with research context using REST API"""
        
        prompt = f"""You are a PM Agent in a standardized multi-agent workflow.

CRITICAL OUTPUT REQUIREMENT: You MUST return a complete standardized Jira ticket JSON based on Jira REST API v3 specifications.

User Request: {user_request}

Research Context:
{research_context}

Your response must be EXACTLY this JSON structure:
```json
{{
  "jira_ticket": {{
    "fields": {{
      "project": {{"key": "AHSSI"}},
      "summary": "Clear action-oriented summary here",
      "description": {{
        "type": "doc",
        "version": 1,
        "content": [
          {{
            "type": "heading",
            "attrs": {{"level": 2}},
            "content": [{{"type": "text", "text": "📋 Business Requirement"}}]
          }},
          {{
            "type": "paragraph", 
            "content": [{{"type": "text", "text": "Detailed business requirement description based on research"}}]
          }},
          {{
            "type": "heading",
            "attrs": {{"level": 3}}, 
            "content": [{{"type": "text", "text": "✅ Acceptance Criteria"}}]
          }},
          {{
            "type": "bulletList",
            "content": [
              {{
                "type": "listItem",
                "content": [{{"type": "paragraph", "content": [{{"type": "text", "text": "Specific acceptance criterion based on research"}}]}}]
              }}
            ]
          }}
        ]
      }},
      "issuetype": {{"name": "Story"}},
      "priority": {{"name": "High"}},
      "labels": ["research-enhanced", "vertex-ai-rest-generated"],
      "customfield_10016": 8
    }}
  }},
  "agent_metadata": {{
    "source_agent": "local_pm_agent_rest",
    "target_agent": "tech_lead_agent",
    "processing_timestamp": "2025-07-07T15:30:00Z",
    "quality_score": 0.85,
    "research_sources": ["gitbook"],
    "business_value": "Clear business value statement based on research",
    "api_method": "rest"
  }}
}}
```

Use the research context to create relevant, informed content. Return ONLY the JSON, no other text."""

        return await self.call_vertex_ai_rest(prompt)
    
    def _format_standardized_output(self, ai_response: str, gitbook_results: Dict) -> Dict[str, Any]:
        """Format AI response as standardized output"""
        
        try:
            # Extract JSON from AI response
            if "```json" in ai_response:
                json_start = ai_response.find("```json") + 7
                json_end = ai_response.find("```", json_start)
                json_content = ai_response[json_start:json_end].strip()
            else:
                json_content = ai_response.strip()
            
            # Parse JSON
            parsed_json = json.loads(json_content)
            
            # Add research metadata
            if "agent_metadata" in parsed_json:
                parsed_json["agent_metadata"]["research_enrichment"] = {
                    "gitbook_sources": len(gitbook_results.get("items", [])),
                    "research_timestamp": "2025-07-07T15:30:00Z",
                    "api_method": "rest"
                }
            
            return parsed_json
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse AI JSON response: {e}")
            logger.error(f"AI Response: {ai_response[:500]}...")
            raise Exception(f"Invalid JSON from AI: {str(e)}")


# Global instance
simple_local_pm_agent_rest = SimpleLocalPMAgentREST()


async def test_local_pm_agent_rest():
    """Simple test of the local PM agent with REST API"""
    test_request = "As a user, I want to implement single sign-on so that I can access multiple systems easily"
    
    try:
        result = await simple_local_pm_agent_rest.process_with_research(test_request)
        print("✅ Local PM Agent (REST) test successful")
        print(f"Title: {result.get('jira_ticket', {}).get('fields', {}).get('summary', 'N/A')}")
        print(f"API Method: {result.get('agent_metadata', {}).get('api_method', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Local PM Agent (REST) test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_local_pm_agent_rest())
    print(f"Test result: {'PASS' if success else 'FAIL'}")