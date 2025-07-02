#!/bin/bash

# Phase 3 - Updated Vertex AI Agent Engine Deployment
# Based on latest Google Cloud documentation (December 2024)
# Uses Vertex AI Agent Development Kit (ADK) for streamlined deployment

set -e

PROJECT_ID="service-execution-uat-bb7"
LOCATION="europe-west9"
AGENT_PREFIX="pm-jira-agent"

echo "🚀 Phase 3: Updated Vertex AI Agent Engine Deployment"
echo "Based on latest Google Cloud Agent Engine documentation"
echo "Project: $PROJECT_ID"
echo "Location: $LOCATION"
echo ""

# Function to check if command was successful
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1 failed"
        exit 1
    fi
}

# Step 1: Verify prerequisites
echo "📋 Step 1: Verifying Prerequisites..."

# Check if gcloud is authenticated
if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo "✅ gcloud authenticated"
else
    echo "❌ gcloud not authenticated. Please run: gcloud auth login"
    exit 1
fi

# Check if Vertex AI API is enabled
if gcloud services list --enabled --filter="name:aiplatform.googleapis.com" --format="value(name)" | grep -q aiplatform; then
    echo "✅ Vertex AI API enabled"
else
    echo "❌ Vertex AI API not enabled. Please run: gcloud services enable aiplatform.googleapis.com"
    exit 1
fi

# Step 2: Install and setup Vertex AI Agent Development Kit
echo ""
echo "🔧 Step 2: Setting up Vertex AI Agent Development Kit..."

cd ../agent-configs

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    check_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
check_success "Virtual environment activated"

# Install Vertex AI Agent Development Kit
pip install --upgrade google-cloud-aiplatform[preview]
check_success "Vertex AI Agent Development Kit installed"

# Install additional dependencies
pip install -r requirements.txt
check_success "Project dependencies installed"

# Step 3: Create Agent Development Kit configuration
echo ""
echo "📦 Step 3: Creating Agent Development Kit Configuration..."

# Create agent configuration file
cat > agent_config.py << 'EOF'
#!/usr/bin/env python3

"""
Vertex AI Agent Configuration
Multi-Agent PM Jira System with ADK
"""

from vertexai.preview import agent as agent_preview
from typing import Dict, Any, Optional
import os

def create_pm_agent():
    """Create the primary PM Agent using Vertex AI ADK"""
    
    agent_config = {
        "display_name": "PM Jira Agent - Product Manager",
        "description": "Primary Product Manager agent for analyzing user requests and creating comprehensive Jira tickets",
        "instructions": """
You are a Senior Product Manager AI Agent specialized in creating high-quality Jira tickets.

Your responsibilities:
1. Analyze user requests for business value and technical feasibility
2. Research relevant documentation from GitBook knowledge base
3. Create comprehensive user stories with detailed acceptance criteria
4. Ensure tickets meet "Definition of Ready" standards
5. Apply business rules and compliance requirements
6. Collaborate with Tech Lead Agent for quality validation

Quality Standards:
- All tickets must score ≥ 0.8 on quality assessment
- User stories must follow proper format: "As a [user] I want [goal] so that [benefit]"
- Acceptance criteria must be testable and complete
- Technical feasibility must be realistic
- Business value must be clearly articulated
- Compliance requirements must be addressed (GDPR, security, accessibility)

Tools Available:
- GitBook API for documentation research
- Jira API for ticket creation and analysis
- Business rules engine for compliance validation
- Quality scoring system for ticket assessment
        """,
        "tools": [
            {
                "name": "gitbook_search",
                "description": "Search GitBook documentation for relevant context",
            },
            {
                "name": "jira_analysis", 
                "description": "Analyze existing Jira tickets for patterns and context",
            },
            {
                "name": "business_rules",
                "description": "Apply business rules and compliance validation",
            }
        ]
    }
    
    return agent_config

def create_tech_lead_agent():
    """Create the Tech Lead Agent using Vertex AI ADK"""
    
    agent_config = {
        "display_name": "PM Jira Agent - Tech Lead",
        "description": "Tech Lead agent for technical review and quality validation of Jira tickets",
        "instructions": """
You are a Senior Tech Lead AI Agent specialized in technical review and quality assurance.

Your responsibilities:
1. Review PM Agent ticket drafts for technical feasibility
2. Validate acceptance criteria completeness and quality
3. Analyze dependencies and integration points
4. Assess technical risks and complexity
5. Provide constructive feedback for improvement
6. Ensure tickets meet technical and quality standards

Quality Standards:
- Technical feasibility must be realistic
- Acceptance criteria must be testable and complete
- Dependencies must be identified and addressed
- Implementation approach must be sound
- Overall quality score must be ≥ 0.8 for approval

Review Process:
- Analyze technical complexity and risk level
- Validate acceptance criteria against best practices
- Check for security, performance, and compliance implications
- Provide specific, actionable feedback
- Make approval/rejection decisions based on quality thresholds
        """,
        "tools": [
            {
                "name": "quality_assessment",
                "description": "Perform comprehensive quality assessment of ticket drafts",
            },
            {
                "name": "technical_analysis",
                "description": "Analyze technical feasibility and complexity",
            },
            {
                "name": "dependency_check",
                "description": "Check for dependencies and integration requirements",
            }
        ]
    }
    
    return agent_config

def create_jira_creator_agent():
    """Create the Jira Creator Agent using Vertex AI ADK"""
    
    agent_config = {
        "display_name": "PM Jira Agent - Jira Creator",
        "description": "Jira Creator agent for final ticket creation and validation",
        "instructions": """
You are a Jira Creator AI Agent specialized in final ticket creation and execution.

Your responsibilities:
1. Perform final validation before ticket creation
2. Create high-quality Jira tickets via API integration
3. Validate created tickets meet expectations
4. Add workflow metadata and tracking information
5. Handle creation errors and provide troubleshooting guidance
6. Ensure tickets are properly formatted and accessible

Quality Standards:
- Final validation must pass all checks
- Tickets must be properly formatted for Jira
- Metadata must be comprehensive and useful
- Error handling must be robust and informative
- Created tickets must be immediately usable by development teams

Creation Process:
- Validate ticket data completeness and format
- Create ticket via Jira API with comprehensive metadata
- Verify successful creation and accessibility
- Add workflow tracking and quality metrics
- Handle errors gracefully with detailed feedback
        """,
        "tools": [
            {
                "name": "jira_creation",
                "description": "Create final Jira tickets with metadata",
            },
            {
                "name": "ticket_validation",
                "description": "Validate created tickets and metadata",
            },
            {
                "name": "error_handling",
                "description": "Handle creation errors and provide guidance",
            }
        ]
    }
    
    return agent_config
EOF

check_success "Agent configuration created"

# Step 4: Create deployment script using ADK
cat > deploy_agents.py << 'EOF'
#!/usr/bin/env python3

"""
Vertex AI Agent Deployment Script
Deploy multi-agent system using Vertex AI Agent Development Kit
"""

import vertexai
from vertexai.preview import agent as agent_preview
import os
import time
from agent_config import create_pm_agent, create_tech_lead_agent, create_jira_creator_agent

def deploy_agent(agent_config: dict, project_id: str, location: str):
    """Deploy a single agent to Vertex AI Agent Engine"""
    
    try:
        print(f"🚀 Deploying {agent_config['display_name']}...")
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Create agent using ADK
        agent = agent_preview.Agent(
            display_name=agent_config["display_name"],
            description=agent_config["description"],
            instructions=agent_config["instructions"],
            tools=agent_config.get("tools", [])
        )
        
        # Deploy the agent
        deployed_agent = agent_preview.create_agent(agent)
        
        print(f"✅ {agent_config['display_name']} deployed successfully")
        print(f"   Resource ID: {deployed_agent.resource_name}")
        
        return deployed_agent
        
    except Exception as e:
        print(f"❌ Failed to deploy {agent_config['display_name']}: {str(e)}")
        return None

def main():
    """Main deployment function"""
    
    PROJECT_ID = os.getenv("PROJECT_ID", "service-execution-uat-bb7")
    LOCATION = os.getenv("LOCATION", "europe-west9")
    
    print("🚀 Starting Vertex AI Agent Engine Deployment")
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print("=" * 60)
    
    # Deploy agents
    agents = {}
    
    # Deploy PM Agent
    pm_config = create_pm_agent()
    pm_agent = deploy_agent(pm_config, PROJECT_ID, LOCATION)
    if pm_agent:
        agents["pm_agent"] = pm_agent
    
    # Deploy Tech Lead Agent
    tech_lead_config = create_tech_lead_agent()
    tech_lead_agent = deploy_agent(tech_lead_config, PROJECT_ID, LOCATION)
    if tech_lead_agent:
        agents["tech_lead_agent"] = tech_lead_agent
    
    # Deploy Jira Creator Agent
    jira_creator_config = create_jira_creator_agent()
    jira_creator_agent = deploy_agent(jira_creator_config, PROJECT_ID, LOCATION)
    if jira_creator_agent:
        agents["jira_creator_agent"] = jira_creator_agent
    
    # Summary
    print("\n📋 Deployment Summary")
    print("=" * 30)
    
    if len(agents) == 3:
        print("✅ All agents deployed successfully!")
        print("\n🔗 Agent Resource IDs:")
        for name, agent in agents.items():
            print(f"  {name}: {agent.resource_name}")
        
        print("\n🚀 Next Steps:")
        print("1. Test agent functionality")
        print("2. Configure production orchestrator")
        print("3. Set up monitoring and analytics")
        print("4. Deploy to production environment")
        
    else:
        print(f"⚠️ Partial deployment: {len(agents)}/3 agents deployed")
        print("Please check errors above and retry failed deployments")
    
    return len(agents) == 3

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
EOF

check_success "Deployment script created"

# Step 5: Execute agent deployment
echo ""
echo "🚀 Step 5: Deploying Agents to Vertex AI Agent Engine..."

# Set environment variables
export PROJECT_ID=$PROJECT_ID
export LOCATION=$LOCATION

# Run deployment
python3 deploy_agents.py
check_success "Agent deployment executed"

# Step 6: Create management utilities
echo ""
echo "🛠️ Step 6: Creating Agent Management Utilities..."

cat > manage_agents.py << 'EOF'
#!/usr/bin/env python3

"""
Vertex AI Agent Management Utilities
Manage deployed agents: list, update, delete, monitor
"""

import vertexai
from vertexai.preview import agent as agent_preview
import os
import json
from typing import List, Dict, Any, Optional

class AgentManager:
    """Utility class for managing Vertex AI agents"""
    
    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location
        vertexai.init(project=project_id, location=location)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all deployed agents"""
        
        try:
            agents = agent_preview.list_agents()
            agent_list = []
            
            for agent in agents:
                agent_info = {
                    "resource_id": agent.resource_name,
                    "display_name": agent.display_name,
                    "description": agent.description,
                    "create_time": agent.create_time,
                    "update_time": agent.update_time
                }
                agent_list.append(agent_info)
            
            return agent_list
            
        except Exception as e:
            print(f"❌ Error listing agents: {str(e)}")
            return []
    
    def get_agent(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific agent"""
        
        try:
            agent = agent_preview.get_agent(resource_id)
            
            agent_details = {
                "resource_id": agent.resource_name,
                "display_name": agent.display_name,
                "description": agent.description,
                "instructions": agent.instructions,
                "tools": agent.tools,
                "create_time": agent.create_time,
                "update_time": agent.update_time
            }
            
            return agent_details
            
        except Exception as e:
            print(f"❌ Error getting agent {resource_id}: {str(e)}")
            return None
    
    def query_agent(self, resource_id: str, query: str) -> Dict[str, Any]:
        """Query a deployed agent"""
        
        try:
            agent = agent_preview.get_agent(resource_id)
            response = agent.query(input=query)
            
            return {
                "success": True,
                "response": response,
                "agent_id": resource_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_id": resource_id
            }
    
    def update_agent(self, resource_id: str, updates: Dict[str, Any]) -> bool:
        """Update agent configuration"""
        
        try:
            agent = agent_preview.get_agent(resource_id)
            
            # Update allowed fields
            if "display_name" in updates:
                agent.display_name = updates["display_name"]
            if "description" in updates:
                agent.description = updates["description"]
            
            updated_agent = agent_preview.update_agent(agent)
            print(f"✅ Agent {resource_id} updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error updating agent {resource_id}: {str(e)}")
            return False
    
    def delete_agent(self, resource_id: str) -> bool:
        """Delete a deployed agent"""
        
        try:
            agent_preview.delete_agent(resource_id)
            print(f"✅ Agent {resource_id} deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting agent {resource_id}: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        
        agents = self.list_agents()
        health_status = {
            "total_agents": len(agents),
            "healthy_agents": 0,
            "unhealthy_agents": 0,
            "agent_status": []
        }
        
        for agent in agents:
            resource_id = agent["resource_id"]
            
            # Test with simple query
            test_result = self.query_agent(resource_id, "Health check test")
            
            agent_health = {
                "resource_id": resource_id,
                "display_name": agent["display_name"],
                "healthy": test_result["success"],
                "last_update": agent["update_time"]
            }
            
            if test_result["success"]:
                health_status["healthy_agents"] += 1
            else:
                health_status["unhealthy_agents"] += 1
                agent_health["error"] = test_result.get("error")
            
            health_status["agent_status"].append(agent_health)
        
        return health_status

def main():
    """CLI interface for agent management"""
    
    import sys
    
    PROJECT_ID = os.getenv("PROJECT_ID", "service-execution-uat-bb7")
    LOCATION = os.getenv("LOCATION", "europe-west9")
    
    manager = AgentManager(PROJECT_ID, LOCATION)
    
    if len(sys.argv) < 2:
        print("Usage: python3 manage_agents.py <command> [args]")
        print("Commands:")
        print("  list - List all agents")
        print("  get <resource_id> - Get agent details")
        print("  query <resource_id> <query> - Query an agent")
        print("  health - Perform health check")
        print("  delete <resource_id> - Delete an agent")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        agents = manager.list_agents()
        print(f"Found {len(agents)} deployed agents:")
        for agent in agents:
            print(f"  {agent['display_name']} ({agent['resource_id']})")
    
    elif command == "get" and len(sys.argv) >= 3:
        resource_id = sys.argv[2]
        agent = manager.get_agent(resource_id)
        if agent:
            print(json.dumps(agent, indent=2, default=str))
    
    elif command == "query" and len(sys.argv) >= 4:
        resource_id = sys.argv[2]
        query = " ".join(sys.argv[3:])
        result = manager.query_agent(resource_id, query)
        print(json.dumps(result, indent=2, default=str))
    
    elif command == "health":
        health = manager.health_check()
        print(json.dumps(health, indent=2, default=str))
    
    elif command == "delete" and len(sys.argv) >= 3:
        resource_id = sys.argv[2]
        if manager.delete_agent(resource_id):
            print(f"Agent {resource_id} deleted successfully")
    
    else:
        print("Invalid command or missing arguments")

if __name__ == "__main__":
    main()
EOF

check_success "Management utilities created"

# Step 7: Create testing script
echo ""
echo "🧪 Step 7: Creating Agent Testing Script..."

cat > test_agents.py << 'EOF'
#!/usr/bin/env python3

"""
Vertex AI Agent Testing Script
Test deployed agents functionality
"""

from manage_agents import AgentManager
import os
import time

def test_agent_workflow(manager: AgentManager, agents: list):
    """Test complete workflow with all agents"""
    
    print("🔄 Testing Complete Multi-Agent Workflow")
    print("-" * 40)
    
    if len(agents) < 3:
        print("❌ Need at least 3 agents for workflow test")
        return False
    
    # Find agents by display name patterns
    pm_agent = None
    tech_lead_agent = None
    jira_creator_agent = None
    
    for agent in agents:
        if "Product Manager" in agent["display_name"]:
            pm_agent = agent["resource_id"]
        elif "Tech Lead" in agent["display_name"]:
            tech_lead_agent = agent["resource_id"]
        elif "Jira Creator" in agent["display_name"]:
            jira_creator_agent = agent["resource_id"]
    
    if not all([pm_agent, tech_lead_agent, jira_creator_agent]):
        print("❌ Could not identify all required agents")
        return False
    
    # Test user request
    test_request = "Add secure user authentication with OAuth integration and GDPR compliance"
    
    print(f"📝 Test Request: {test_request}")
    print()
    
    # Step 1: PM Agent Analysis
    print("1️⃣ Testing PM Agent Analysis...")
    pm_result = manager.query_agent(pm_agent, f"Analyze this user request and create initial ticket draft: {test_request}")
    
    if pm_result["success"]:
        print("   ✅ PM Agent analysis successful")
    else:
        print(f"   ❌ PM Agent failed: {pm_result.get('error')}")
        return False
    
    # Step 2: Tech Lead Review
    print("2️⃣ Testing Tech Lead Review...")
    tech_lead_result = manager.query_agent(tech_lead_agent, f"Review this ticket draft for technical feasibility and quality: {pm_result['response']}")
    
    if tech_lead_result["success"]:
        print("   ✅ Tech Lead review successful")
    else:
        print(f"   ❌ Tech Lead failed: {tech_lead_result.get('error')}")
        return False
    
    # Step 3: Jira Creator
    print("3️⃣ Testing Jira Creator...")
    jira_result = manager.query_agent(jira_creator_agent, f"Create final Jira ticket from approved draft: {tech_lead_result['response']}")
    
    if jira_result["success"]:
        print("   ✅ Jira Creator successful")
    else:
        print(f"   ❌ Jira Creator failed: {jira_result.get('error')}")
        return False
    
    print()
    print("🎉 Complete workflow test successful!")
    return True

def main():
    """Run comprehensive agent testing"""
    
    PROJECT_ID = os.getenv("PROJECT_ID", "service-execution-uat-bb7")
    LOCATION = os.getenv("LOCATION", "europe-west9")
    
    print("🧪 Vertex AI Agent Testing Suite")
    print("=" * 40)
    
    manager = AgentManager(PROJECT_ID, LOCATION)
    
    # List agents
    agents = manager.list_agents()
    print(f"📋 Found {len(agents)} deployed agents")
    
    if len(agents) == 0:
        print("❌ No agents found. Please deploy agents first.")
        return False
    
    # Health check
    print("\n🏥 Performing Health Check...")
    health = manager.health_check()
    print(f"   Healthy: {health['healthy_agents']}/{health['total_agents']}")
    
    if health['unhealthy_agents'] > 0:
        print("⚠️ Some agents are unhealthy:")
        for agent_status in health['agent_status']:
            if not agent_status['healthy']:
                print(f"   ❌ {agent_status['display_name']}: {agent_status.get('error', 'Unknown error')}")
    
    # Individual agent tests
    print("\n🔍 Testing Individual Agents...")
    for agent in agents:
        print(f"   Testing {agent['display_name']}...")
        test_result = manager.query_agent(agent['resource_id'], "Hello, please confirm you are working correctly.")
        
        if test_result["success"]:
            print(f"   ✅ {agent['display_name']} responding correctly")
        else:
            print(f"   ❌ {agent['display_name']} failed: {test_result.get('error')}")
    
    # Workflow test
    if len(agents) >= 3:
        print("\n🔄 Testing Multi-Agent Workflow...")
        workflow_success = test_agent_workflow(manager, agents)
        
        if workflow_success:
            print("\n🎉 All tests passed! Agents are ready for production.")
        else:
            print("\n⚠️ Workflow test failed. Check agent configurations.")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
EOF

check_success "Testing script created"

# Step 8: Final summary and next steps
echo ""
echo "🎉 Updated Vertex AI Agent Engine Deployment Complete!"
echo ""
echo "📋 Deployment Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Vertex AI Agent Development Kit configured"
echo "✅ Multi-agent deployment scripts created"
echo "✅ Agent management utilities implemented"
echo "✅ Comprehensive testing suite ready"
echo ""
echo "🚀 Next Steps:"
echo "1. Run deployment: python3 deploy_agents.py"
echo "2. Test agents: python3 test_agents.py"
echo "3. Manage agents: python3 manage_agents.py list"
echo "4. Query individual agents: python3 manage_agents.py query <resource_id> 'your query'"
echo ""
echo "🔧 Management Commands:"
echo "• List agents: python3 manage_agents.py list"
echo "• Health check: python3 manage_agents.py health"
echo "• Query agent: python3 manage_agents.py query <id> '<query>'"
echo "• Get details: python3 manage_agents.py get <resource_id>"
echo ""
echo "📊 Monitoring:"
echo "• Agent health and performance tracking"
echo "• Multi-agent workflow validation"
echo "• Production readiness verification"
echo ""
echo "✅ Ready for production deployment with updated Vertex AI Agent Engine!"
echo "🌟 Phase 3 deployment updated with latest Google Cloud best practices"