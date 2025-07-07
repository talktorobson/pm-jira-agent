#!/usr/bin/env python3
"""
Test Direct GitBook Content Retrieval - Bypass agent search strategies
"""

import asyncio
import json
import httpx
from enhanced_multi_agent_orchestrator import EnhancedMultiAgentOrchestrator

async def test_direct_gitbook_content():
    """Test direct GitBook content retrieval with known working terms"""
    
    print("🔍 DIRECT GITBOOK CONTENT TEST")
    print("="*60)
    
    # Initialize orchestrator for credentials
    orchestrator = EnhancedMultiAgentOrchestrator()
    
    headers = {
        "Authorization": f"Bearer {orchestrator.gitbook_config['token']}",
        "Content-Type": "application/json"
    }
    
    # Use EXACT simple terms that worked in our earlier direct tests
    direct_searches = ["service", "Pyxis", "AHS"]
    
    async with httpx.AsyncClient() as client:
        
        successful_content = []
        
        for term in direct_searches:
            print(f"\n🔍 DIRECT SEARCH: '{term}'")
            print("-"*40)
            
            try:
                # Direct search without agent strategy modifications
                response = await client.get(
                    f"{orchestrator.gitbook_config['base_url']}/spaces/{orchestrator.gitbook_config['space_id']}/search",
                    headers=headers,
                    params={"query": term, "limit": 5},
                    timeout=10.0
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    print(f"   Results: {len(items)} items")
                    
                    for i, item in enumerate(items):
                        title = item.get('title', 'No Title')
                        item_id = item.get('id', None)
                        
                        print(f"\n   📄 Item {i+1}: {title}")
                        print(f"      ID: {item_id}")
                        
                        if item_id:
                            # Get full content
                            print(f"      🔍 Fetching full content...")
                            content_response = await client.get(
                                f"{orchestrator.gitbook_config['base_url']}/spaces/{orchestrator.gitbook_config['space_id']}/content/page/{item_id}",
                                headers=headers,
                                timeout=10.0
                            )
                            
                            if content_response.status_code == 200:
                                content_data = content_response.json()
                                full_text = extract_text_content(content_data)
                                word_count = len(full_text.split()) if full_text else 0
                                
                                print(f"      ✅ Content Retrieved: {word_count} words")
                                print(f"      📝 Content: {full_text}")
                                
                                if word_count > 5:  # Only save meaningful content
                                    successful_content.append({
                                        'search_term': term,
                                        'title': title,
                                        'page_id': item_id,
                                        'full_content': full_text,
                                        'word_count': word_count
                                    })
                            else:
                                print(f"      ❌ Content fetch failed: {content_response.status_code}")
                        else:
                            print(f"      ❌ No page ID available")
                
            except Exception as e:
                print(f"   💥 Search error: {e}")
        
        # Summary and test PM Agent with best content
        print(f"\n📊 CONTENT RETRIEVAL SUMMARY:")
        print(f"   Total Searches: {len(direct_searches)}")
        print(f"   Successful Content: {len(successful_content)}")
        
        if successful_content:
            print(f"\n✅ PAGES WITH FULL CONTENT:")
            for i, content in enumerate(successful_content, 1):
                print(f"   {i}. {content['title']} ({content['word_count']} words)")
                print(f"      Search Term: '{content['search_term']}'")
                print(f"      Content: {content['full_content'][:100]}...")
                print()
            
            # Test PM Agent with the best content
            best_content = successful_content[0]
            print(f"🤖 TESTING PM AGENT WITH BEST CONTENT:")
            print(f"   Using: {best_content['title']}")
            
            # Create enhanced prompt with full GitBook content
            enhanced_prompt = f"""
            Create a professional Jira ticket to enhance the system described in this GitBook documentation.
            
            GITBOOK DOCUMENTATION:
            Title: {best_content['title']}
            Content: {best_content['full_content']}
            
            Based on this documentation, create a ticket that:
            1. References the specific system components mentioned
            2. Addresses potential improvements or enhancements
            3. Uses the business context from the documentation
            4. Creates actionable requirements
            
            Generate a professional Jira ticket with summary, description, and acceptance criteria.
            """
            
            # Call PM Agent
            pm_result = await orchestrator.call_vertex_ai_agent(
                orchestrator.agents["pm_agent"],
                "pm_agent",
                enhanced_prompt
            )
            
            if pm_result.get('success'):
                print(f"   ✅ PM AGENT SUCCESS WITH FULL GITBOOK CONTENT!")
                
                response = pm_result.get('response', {})
                if isinstance(response, dict):
                    summary = response.get('summary', 'GitBook Enhanced Ticket')
                    description = response.get('description', 'Enhanced with GitBook content')
                    
                    print(f"   📋 Summary: {summary}")
                    print(f"   📄 Description: {description[:200]}...")
                    
                    # Create real ticket
                    print(f"\n🎫 CREATING REAL JIRA TICKET:")
                    
                    ticket_result = await create_ticket_with_gitbook_content(
                        orchestrator, response, best_content
                    )
                    
                    if ticket_result.get('success'):
                        print(f"   🎉 SUCCESS! Ticket created with full GitBook content!")
                        print(f"   🎫 Ticket: {ticket_result['ticket_key']}")
                        print(f"   🔗 URL: {ticket_result['ticket_url']}")
                        
                        # Save complete success
                        complete_success = {
                            "timestamp": "2025-07-07T23:05:00Z",
                            "test_type": "Direct GitBook Full Content Success",
                            "gitbook_content": best_content,
                            "pm_agent_response": pm_result,
                            "ticket_creation": ticket_result,
                            "achievement": "PM Agent successfully used full GitBook content to create real ticket"
                        }
                        
                        with open("gitbook_full_content_success.json", "w") as f:
                            json.dump(complete_success, f, indent=2)
                        
                        print(f"\n🎯 COMPLETE SUCCESS!")
                        print(f"   ✅ GitBook Full Content: Retrieved and used")
                        print(f"   ✅ PM Agent Enhancement: Working with documentation")
                        print(f"   ✅ Real Ticket Created: {ticket_result['ticket_key']}")
                        print(f"   📄 Results: gitbook_full_content_success.json")
                        
                    else:
                        print(f"   ❌ Ticket creation failed: {ticket_result.get('error')}")
                else:
                    print(f"   📄 Response: {str(response)[:200]}...")
            else:
                print(f"   ❌ PM Agent failed: {pm_result.get('error')}")
        else:
            print(f"❌ No meaningful content retrieved")

def extract_text_content(content_data):
    """Extract text from GitBook content"""
    def extract_from_node(node):
        if isinstance(node, dict):
            text_parts = []
            
            if node.get('type') == 'text' and 'text' in node:
                text_parts.append(node['text'])
            
            if 'document' in node:
                text_parts.append(extract_from_node(node['document']))
            
            if 'content' in node:
                if isinstance(node['content'], list):
                    for child in node['content']:
                        text_parts.append(extract_from_node(child))
                else:
                    text_parts.append(extract_from_node(node['content']))
            
            if 'children' in node:
                for child in node['children']:
                    text_parts.append(extract_from_node(child))
            
            if 'title' in node:
                text_parts.append(node['title'])
            if 'description' in node:
                text_parts.append(node['description'])
                
            return ' '.join(filter(None, text_parts))
        
        elif isinstance(node, list):
            return ' '.join(extract_from_node(item) for item in node)
        
        elif isinstance(node, str):
            return node
            
        return ''
    
    return extract_from_node(content_data)

async def create_ticket_with_gitbook_content(orchestrator, pm_response, gitbook_content):
    """Create Jira ticket highlighting GitBook content usage"""
    
    try:
        headers = {
            "Authorization": f"Bearer {orchestrator.jira_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Extract ticket details
        if isinstance(pm_response, dict):
            summary = pm_response.get('summary', 'GitBook Enhanced System Improvement')
            base_description = pm_response.get('description', 'AI-generated enhancement')
        else:
            summary = 'GitBook Enhanced System Improvement'
            base_description = str(pm_response)
        
        # Enhanced description with GitBook context
        enhanced_description = f"""
{base_description}

--- GITBOOK DOCUMENTATION SOURCE ---
Title: {gitbook_content['title']}
Content: {gitbook_content['full_content']}

This ticket was generated using FULL GitBook documentation content, demonstrating the PM Agent's ability to leverage complete documentation context for informed ticket creation.
"""
        
        jira_payload = {
            "fields": {
                "project": {"key": "AHSSI"},
                "summary": f"[GitBook Enhanced] {summary}"[:200],
                "description": enhanced_description[:2000],
                "issuetype": {"name": "Story"},
                "priority": {"name": "Medium"},
                "labels": ["gitbook-full-content", "documentation-based", "pm-agent-enhanced"]
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{orchestrator.jira_config['base_url']}/rest/api/{orchestrator.jira_config['api_version']}/issue",
                headers=headers,
                json=jira_payload,
                timeout=30.0
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    "success": True,
                    "ticket_key": result.get("key"),
                    "ticket_url": f"{orchestrator.jira_config['base_url']}/browse/{result.get('key')}",
                    "enhanced_with_gitbook": True
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asyncio.run(test_direct_gitbook_content())