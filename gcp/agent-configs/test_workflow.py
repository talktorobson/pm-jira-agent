#!/usr/bin/env python3

"""
Test workflow for PM Jira Agent Multi-Agent System
Tests the complete multi-agent workflow with sample requests
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any

# Add the agent-configs directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import create_jira_ticket_with_ai, MultiAgentOrchestrator
from tools import CloudFunctionTools, QualityGates

def test_cloud_function_connectivity():
    """Test connectivity to deployed Cloud Functions"""
    print("🔧 Testing Cloud Function Connectivity...")
    
    tools = CloudFunctionTools()
    
    # Test GitBook API
    print("\n📚 Testing GitBook API...")
    gitbook_result = tools.search_gitbook_content("integration")
    if gitbook_result["success"]:
        print("✅ GitBook API: Connected and working")
        print(f"   Content length: {len(gitbook_result['content'])}")
    else:
        print(f"❌ GitBook API: {gitbook_result['error']}")
    
    # Test Jira API
    print("\n🎫 Testing Jira API...")
    jira_result = tools.analyze_existing_jira_tickets()
    if jira_result["success"]:
        print("✅ Jira API: Connected and working")
        print(f"   Tickets analyzed: {jira_result['ticket_count']}")
    else:
        print(f"❌ Jira API: {jira_result['error']}")
    
    return gitbook_result["success"] and jira_result["success"]

def test_quality_gates():
    """Test quality assessment system"""
    print("\n🎯 Testing Quality Gates...")
    
    # Test ticket with good quality
    good_ticket = {
        "summary": "Implement user authentication system",
        "description": """As a user I want to securely log into the system so that I can access my personal data.

Acceptance Criteria:
• User can log in with email and password
• System validates credentials securely  
• User receives appropriate error messages for invalid login
• Session is maintained for 24 hours
• User can log out successfully""",
        "issue_type": "Story",
        "priority": "High"
    }
    
    quality_result = QualityGates.calculate_quality_score(good_ticket)
    print(f"Good ticket quality score: {quality_result['overall_score']}")
    print(f"Passes quality gate: {quality_result['passes_quality_gate']}")
    
    # Test ticket with poor quality
    poor_ticket = {
        "summary": "Fix stuff",
        "description": "Something is broken",
        "issue_type": "Bug"
    }
    
    poor_quality_result = QualityGates.calculate_quality_score(poor_ticket)
    print(f"Poor ticket quality score: {poor_quality_result['overall_score']}")
    print(f"Passes quality gate: {poor_quality_result['passes_quality_gate']}")
    
    return quality_result['passes_quality_gate'] and not poor_quality_result['passes_quality_gate']

def test_sample_requests():
    """Test the complete workflow with sample user requests"""
    print("\n🤖 Testing Complete Multi-Agent Workflow...")
    
    sample_requests = [
        {
            "request": "Add a search feature to help users find products quickly",
            "context": {"priority": "high", "department": "e-commerce"}
        },
        {
            "request": "Fix the slow loading issue on the dashboard page",
            "context": {"urgency": "medium", "affects": "all users"}
        },
        {
            "request": "Integrate with external payment gateway for international customers",
            "context": {"scope": "international", "compliance": "required"}
        }
    ]
    
    results = []
    
    for i, sample in enumerate(sample_requests, 1):
        print(f"\n--- Test Case {i}: {sample['request'][:50]}... ---")
        
        try:
            # Note: This will call the actual multi-agent system
            # In a real test, you might want to mock some components
            result = create_jira_ticket_with_ai(sample["request"], sample["context"])
            
            if result["success"]:
                print(f"✅ Workflow completed successfully")
                print(f"   Quality score: {result.get('quality_metrics', {}).get('final_quality_score', 'N/A')}")
                print(f"   Iterations: {result.get('quality_metrics', {}).get('iterations_required', 'N/A')}")
                print(f"   Ticket created: {result.get('ticket_created', False)}")
                if result.get('ticket_key'):
                    print(f"   Ticket key: {result['ticket_key']}")
            else:
                print(f"❌ Workflow failed: {result.get('failure_reason', 'Unknown error')}")
            
            results.append(result)
            
        except Exception as e:
            print(f"❌ Test case {i} failed with exception: {str(e)}")
            results.append({"success": False, "error": str(e)})
    
    return results

def test_individual_agents():
    """Test individual agent functionality"""
    print("\n🎭 Testing Individual Agents...")
    
    # Test imports
    try:
        from pm_agent import PMAgent
        from tech_lead_agent import TechLeadAgent  
        from jira_agent import JiraCreatorAgent
        print("✅ All agent classes imported successfully")
        
        # Test agent initialization
        pm_agent = PMAgent()
        tech_lead_agent = TechLeadAgent()
        jira_agent = JiraCreatorAgent()
        print("✅ All agents initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent testing failed: {str(e)}")
        return False

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("🚀 PM Jira Agent Multi-Agent System - Comprehensive Test")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: Cloud Function Connectivity
    test_results["cloud_functions"] = test_cloud_function_connectivity()
    
    # Test 2: Quality Gates
    test_results["quality_gates"] = test_quality_gates()
    
    # Test 3: Individual Agents
    test_results["individual_agents"] = test_individual_agents()
    
    # Test 4: Sample Workflow (optional - can be resource intensive)
    print("\n" + "=" * 60)
    print("⚠️  Sample Workflow Test (Optional)")
    print("This test will actually call the multi-agent system and may:")
    print("- Make real API calls to GitBook and Jira")
    print("- Create actual Jira tickets (in test mode)")
    print("- Take 2-5 minutes to complete")
    
    run_workflow_test = input("\nRun sample workflow test? (y/N): ").lower().strip() == 'y'
    
    if run_workflow_test:
        workflow_results = test_sample_requests()
        test_results["sample_workflows"] = [r["success"] for r in workflow_results]
    else:
        print("⏭️  Skipping sample workflow test")
        test_results["sample_workflows"] = ["skipped"]
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        if test_name == "sample_workflows":
            if result == ["skipped"]:
                print(f"⏭️  {test_name}: Skipped")
            else:
                success_count = sum(1 for r in result if r)
                total_count = len(result)
                print(f"{'✅' if success_count == total_count else '⚠️ '} {test_name}: {success_count}/{total_count} passed")
        else:
            print(f"{'✅' if result else '❌'} {test_name}: {'Passed' if result else 'Failed'}")
    
    # Overall status
    core_tests_passed = all([
        test_results["cloud_functions"],
        test_results["quality_gates"],
        test_results["individual_agents"]
    ])
    
    print("\n" + "=" * 60)
    if core_tests_passed:
        print("🎉 Core system tests PASSED! Multi-agent system is ready for deployment.")
        print("\n📋 Next Steps:")
        print("1. Deploy to Vertex AI Agent Engine (Phase 2 completion)")
        print("2. Set up production monitoring and logging")
        print("3. Configure deployment automation")
        print("4. Begin Phase 3: Advanced features")
    else:
        print("⚠️  Some core tests FAILED. Review errors before deployment.")
        print("\n🔧 Troubleshooting:")
        print("1. Check Cloud Function deployment and connectivity")
        print("2. Verify API credentials in Secret Manager")
        print("3. Ensure virtual environment has all dependencies")
        print("4. Review error logs for specific issues")

if __name__ == "__main__":
    run_comprehensive_test()