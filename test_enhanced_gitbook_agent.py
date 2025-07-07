#!/usr/bin/env python3
"""
Enhanced GitBook Agent - Fetches FULL content from GitBook pages
"""

import asyncio
import json
import logging
import httpx
from datetime import datetime
from enhanced_multi_agent_orchestrator import EnhancedMultiAgentOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedGitBookOrchestrator(EnhancedMultiAgentOrchestrator):
    """
    Enhanced orchestrator that fetches FULL GitBook page content
    """
    
    async def search_gitbook_context_with_full_content(self, query: str, agent_context: str):
        """Search GitBook and fetch FULL content from found pages"""
        
        print(f"\n🔍 ENHANCED GITBOOK SEARCH WITH FULL CONTENT")
        print("="*70)
        print(f"📝 Agent: {agent_context}")
        print(f"📝 Query: '{query}'")
        
        try:
            # First, do the regular search to find pages
            basic_results = await super().search_gitbook_context(query, agent_context)
            
            if not basic_results:
                print("❌ No GitBook pages found in search")
                return []
            
            print(f"📚 Found {len(basic_results)} GitBook pages, fetching full content...")
            
            # Now fetch full content for each page
            enhanced_results = []
            headers = {
                "Authorization": f"Bearer {self.gitbook_config['token']}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                for i, result in enumerate(basic_results):
                    title = result.get('title', 'No Title')
                    print(f"\n📄 Page {i+1}: {title}")
                    
                    # Extract page ID from search results or try to find it
                    page_id = await self._find_page_id(client, headers, title)
                    
                    if page_id:
                        print(f"   📋 Page ID: {page_id}")
                        
                        # Fetch full content
                        full_content = await self._fetch_page_content(client, headers, page_id)
                        
                        if full_content:
                            word_count = len(full_content.split())
                            print(f"   ✅ Full content retrieved: {word_count} words")
                            print(f"   📝 Content: {full_content[:150]}...")
                            
                            # Enhanced result with full content
                            enhanced_result = result.copy()
                            enhanced_result.update({
                                'full_content': full_content,
                                'word_count': word_count,
                                'page_id': page_id,
                                'content_retrieved': True
                            })
                            enhanced_results.append(enhanced_result)
                        else:
                            print(f"   ⚠️ Could not retrieve full content")
                            enhanced_results.append(result)
                    else:
                        print(f"   ❌ Could not find page ID")
                        enhanced_results.append(result)
            
            print(f"\n📊 Enhanced Results: {len(enhanced_results)} pages")
            content_pages = sum(1 for r in enhanced_results if r.get('content_retrieved', False))
            print(f"📊 Pages with Full Content: {content_pages}")
            
            return enhanced_results
            
        except Exception as e:
            print(f"❌ Enhanced GitBook search error: {e}")
            return []
        
        finally:
            print("="*70)
    
    async def _find_page_id(self, client, headers, title):
        """Find page ID by searching for the exact title"""
        
        try:
            # Search for exact title
            response = await client.get(
                f"{self.gitbook_config['base_url']}/spaces/{self.gitbook_config['space_id']}/search",
                headers=headers,
                params={"query": title, "limit": 10},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                # Find exact title match
                for item in items:
                    if item.get('title', '').strip() == title.strip():
                        return item.get('id')
            
            return None
            
        except Exception as e:
            print(f"   ❌ Error finding page ID: {e}")
            return None
    
    async def _fetch_page_content(self, client, headers, page_id):
        """Fetch full content from a GitBook page"""
        
        try:
            response = await client.get(
                f"{self.gitbook_config['base_url']}/spaces/{self.gitbook_config['space_id']}/content/page/{page_id}",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                content_data = response.json()
                text_content = self._extract_text_from_content(content_data)
                return text_content
            else:
                print(f"   ❌ Content fetch failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error fetching content: {e}")
            return None
    
    def _extract_text_from_content(self, content_data):
        """Extract text content from GitBook page data"""
        
        def extract_from_node(node):
            if isinstance(node, dict):
                text_parts = []
                
                # Handle text nodes
                if node.get('type') == 'text' and 'text' in node:
                    text_parts.append(node['text'])
                
                # Handle document structure
                if 'document' in node:
                    text_parts.append(extract_from_node(node['document']))
                
                # Handle content arrays
                if 'content' in node:
                    if isinstance(node['content'], list):
                        for child in node['content']:
                            text_parts.append(extract_from_node(child))
                    else:
                        text_parts.append(extract_from_node(node['content']))
                
                # Handle children arrays
                if 'children' in node:
                    for child in node['children']:
                        text_parts.append(extract_from_node(child))
                
                # Handle title and description
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

async def test_enhanced_gitbook_workflow():
    """Test workflow with enhanced GitBook content retrieval"""
    
    print("🚀 ENHANCED GITBOOK WORKFLOW TEST")
    print("="*80)
    print("🎯 Goal: Test PM agents with FULL GitBook content (not just titles)")
    print("="*80)
    
    # Initialize enhanced orchestrator
    orchestrator = EnhancedGitBookOrchestrator()
    
    # Test request that should match GitBook content
    test_request = """
    Enhance the Service Execution (Sx) system based on current business rules.
    Improve the creation and recreation process for better integration with 
    Pyxis and Tempo systems. Add monitoring and error handling capabilities.
    Priority: High
    Component: Service Execution
    """
    
    print(f"\n📋 Test Request:")
    print(test_request.strip())
    print("\n" + "="*80)
    
    try:
        start_time = datetime.now()
        
        # Test enhanced GitBook search
        print(f"\n🔍 PHASE 1: ENHANCED GITBOOK SEARCH")
        enhanced_gitbook_results = await orchestrator.search_gitbook_context_with_full_content(
            test_request.strip(),
            "pm_agent"
        )
        
        # Compare with basic search
        print(f"\n🔍 PHASE 2: BASIC SEARCH (for comparison)")
        basic_gitbook_results = await orchestrator.search_gitbook_context(
            test_request.strip(),
            "pm_agent"
        )
        
        # Analyze the difference
        print(f"\n📊 COMPARISON ANALYSIS:")
        print(f"   Enhanced Search Results: {len(enhanced_gitbook_results)}")
        print(f"   Basic Search Results: {len(basic_gitbook_results)}")
        
        enhanced_with_content = sum(1 for r in enhanced_gitbook_results if r.get('content_retrieved', False))
        print(f"   Pages with Full Content: {enhanced_with_content}")
        
        if enhanced_with_content > 0:
            print(f"\n📄 FULL CONTENT EXAMPLES:")
            for i, result in enumerate(enhanced_gitbook_results):
                if result.get('content_retrieved', False):
                    print(f"   📋 {result['title']}:")
                    print(f"      Words: {result['word_count']}")
                    print(f"      Content: {result['full_content'][:200]}...")
        
        # Test PM Agent with enhanced GitBook context
        if enhanced_with_content > 0:
            print(f"\n🤖 PHASE 3: PM AGENT WITH ENHANCED GITBOOK CONTEXT")
            
            # Format enhanced GitBook context
            enhanced_context = ""
            for result in enhanced_gitbook_results:
                if result.get('content_retrieved', False):
                    enhanced_context += f"**{result['title']}**:\n{result['full_content']}\n\n"
            
            agent_prompt = f"""
            Create a professional Jira ticket for: {test_request.strip()}
            
            DETAILED GITBOOK DOCUMENTATION CONTEXT:
            {enhanced_context}
            
            Use the detailed GitBook context to create a more informed and specific ticket.
            Reference specific business rules and system components mentioned in the documentation.
            """
            
            # Call PM Agent with enhanced context
            pm_result = await orchestrator.call_vertex_ai_agent(
                orchestrator.agents["pm_agent"],
                "pm_agent",
                agent_prompt
            )
            
            if pm_result.get('success'):
                print(f"   ✅ PM Agent generated ticket with FULL GitBook context")
                response = pm_result.get('response', {})
                
                if isinstance(response, dict):
                    print(f"   📋 Summary: {response.get('summary', 'N/A')}")
                    desc_preview = response.get('description', '')[:200] if response.get('description') else 'N/A'
                    print(f"   📄 Description: {desc_preview}...")
                else:
                    print(f"   📄 Response: {str(response)[:200]}...")
                
                # Save enhanced results
                enhanced_test_results = {
                    "timestamp": datetime.now().isoformat(),
                    "test_type": "Enhanced GitBook Content Test",
                    "request": test_request.strip(),
                    "enhanced_gitbook_results": enhanced_gitbook_results,
                    "basic_gitbook_results": basic_gitbook_results,
                    "pm_agent_response": pm_result,
                    "comparison": {
                        "enhanced_pages": len(enhanced_gitbook_results),
                        "basic_pages": len(basic_gitbook_results),
                        "pages_with_full_content": enhanced_with_content,
                        "content_improvement": enhanced_with_content > 0
                    }
                }
                
                with open("enhanced_gitbook_workflow_test.json", "w") as f:
                    json.dump(enhanced_test_results, f, indent=2)
                
                print(f"\n✅ ENHANCED GITBOOK TEST COMPLETE!")
                print(f"   📄 Results saved to: enhanced_gitbook_workflow_test.json")
                
            else:
                print(f"   ❌ PM Agent failed: {pm_result.get('error', 'Unknown')}")
        else:
            print(f"\n⚠️ No full content retrieved - cannot test enhanced context")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"\n📊 FINAL SUMMARY:")
        print(f"   Duration: {duration:.1f}s")
        print(f"   Enhanced Method: {'✅ Working' if enhanced_with_content > 0 else '❌ No improvement'}")
        print(f"   Content Quality: {'✅ Full content available' if enhanced_with_content > 0 else '⚠️ Limited content'}")
        
    except Exception as e:
        print(f"❌ Enhanced test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_gitbook_workflow())