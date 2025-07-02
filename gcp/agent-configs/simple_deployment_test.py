#!/usr/bin/env python3

"""
Simple Deployment Test for PM Jira Agent
Tests the existing orchestrator with Cloud Functions integration
Validates end-to-end workflow without requiring agent_engines
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the existing orchestrator
try:
    from orchestrator import create_jira_ticket_with_ai
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import orchestrator: {e}")
    ORCHESTRATOR_AVAILABLE = False

def test_cloud_functions() -> Dict[str, Any]:
    """Test Cloud Functions connectivity"""
    
    logger.info("🔧 Testing Cloud Functions connectivity...")
    
    test_results = {
        "gitbook_function": {"status": "unknown", "url": "https://gitbook-api-jlhinciqia-od.a.run.app"},
        "jira_function": {"status": "unknown", "url": "https://jira-api-jlhinciqia-od.a.run.app"}
    }
    
    # Test GitBook function
    try:
        import requests
        
        # Test GitBook function health
        gitbook_response = requests.get(f"{test_results['gitbook_function']['url']}/health", timeout=10)
        if gitbook_response.status_code == 200:
            test_results["gitbook_function"]["status"] = "operational"
            logger.info("✅ GitBook function operational")
        else:
            test_results["gitbook_function"]["status"] = "error"
            test_results["gitbook_function"]["error"] = f"HTTP {gitbook_response.status_code}"
            logger.warning(f"⚠️ GitBook function returned {gitbook_response.status_code}")
            
    except Exception as e:
        test_results["gitbook_function"]["status"] = "error"
        test_results["gitbook_function"]["error"] = str(e)
        logger.error(f"❌ GitBook function test failed: {e}")
    
    # Test Jira function
    try:
        # Test Jira function health
        jira_response = requests.get(f"{test_results['jira_function']['url']}/health", timeout=10)
        if jira_response.status_code == 200:
            test_results["jira_function"]["status"] = "operational"
            logger.info("✅ Jira function operational")
        else:
            test_results["jira_function"]["status"] = "error"
            test_results["jira_function"]["error"] = f"HTTP {jira_response.status_code}"
            logger.warning(f"⚠️ Jira function returned {jira_response.status_code}")
            
    except Exception as e:
        test_results["jira_function"]["status"] = "error"
        test_results["jira_function"]["error"] = str(e)
        logger.error(f"❌ Jira function test failed: {e}")
    
    return test_results

def test_orchestrator() -> Dict[str, Any]:
    """Test the existing multi-agent orchestrator"""
    
    logger.info("🤖 Testing multi-agent orchestrator...")
    
    if not ORCHESTRATOR_AVAILABLE:
        return {
            "status": "error",
            "error": "Orchestrator not available",
            "suggestion": "Check import dependencies"
        }
    
    try:
        # Test with a simple user request
        test_request = "Add secure user authentication with OAuth integration and session management"
        
        logger.info(f"Testing with request: {test_request}")
        
        start_time = time.time()
        result = create_jira_ticket_with_ai(test_request)
        execution_time = time.time() - start_time
        
        test_result = {
            "status": "success" if result.get("success", False) else "partial",
            "execution_time": round(execution_time, 2),
            "result": result,
            "agents_used": result.get("agent_interactions", []),
            "quality_score": result.get("final_quality_score"),
            "ticket_created": result.get("ticket_created", False)
        }
        
        if result.get("success", False):
            logger.info("✅ Orchestrator test successful")
        else:
            logger.warning("⚠️ Orchestrator test completed with issues")
        
        return test_result
        
    except Exception as e:
        logger.error(f"❌ Orchestrator test failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "execution_time": 0
        }

def test_business_rules() -> Dict[str, Any]:
    """Test business rules engine"""
    
    logger.info("📋 Testing business rules engine...")
    
    try:
        from business_rules import BusinessRulesEngine
        
        business_rules = BusinessRulesEngine()
        
        # Test ticket draft
        test_ticket = {
            "summary": "Implement user authentication",
            "description": "As a user I want secure login so that my account is protected",
            "priority": "High",
            "issue_type": "Story"
        }
        
        result = business_rules.apply_business_rules(test_ticket, {})
        
        if result.get("success", False):
            logger.info("✅ Business rules test successful")
            return {
                "status": "success",
                "rules_applied": result.get("rule_results", {}).get("rules_applied", []),
                "enhanced_ticket": result.get("enhanced_ticket", {})
            }
        else:
            logger.warning("⚠️ Business rules test had issues")
            return {
                "status": "partial",
                "error": result.get("error", "Unknown error")
            }
            
    except ImportError:
        logger.warning("⚠️ Business rules engine not available")
        return {
            "status": "not_available",
            "error": "Business rules engine not imported"
        }
    except Exception as e:
        logger.error(f"❌ Business rules test failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def test_monitoring() -> Dict[str, Any]:
    """Test monitoring system"""
    
    logger.info("📊 Testing monitoring system...")
    
    try:
        from monitoring import MonitoringSystem
        
        monitoring = MonitoringSystem("service-execution-uat-bb7")
        
        # Test workflow monitoring
        test_workflow_id = f"test_workflow_{int(time.time())}"
        
        monitoring.start_workflow_monitoring(test_workflow_id, "Test workflow monitoring")
        monitoring.track_agent_execution(test_workflow_id, "Test Agent", 1.5, True, 0.85, 1)
        monitoring.complete_workflow_monitoring(test_workflow_id, True, True, "TEST-123")
        
        logger.info("✅ Monitoring test successful")
        return {
            "status": "success",
            "test_workflow_id": test_workflow_id,
            "monitoring_functional": True
        }
        
    except ImportError:
        logger.warning("⚠️ Monitoring system not available")
        return {
            "status": "not_available",
            "error": "Monitoring system not imported"
        }
    except Exception as e:
        logger.error(f"❌ Monitoring test failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def run_comprehensive_test() -> Dict[str, Any]:
    """Run comprehensive system test"""
    
    print("🚀 PM Jira Agent - Comprehensive System Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    # Initialize test results
    test_results = {
        "test_timestamp": datetime.now().isoformat(),
        "test_duration": 0,
        "components": {},
        "overall_status": "unknown",
        "success_count": 0,
        "total_tests": 4
    }
    
    start_time = time.time()
    
    # Test 1: Cloud Functions
    print("🔧 Test 1: Cloud Functions Connectivity")
    cloud_functions_result = test_cloud_functions()
    test_results["components"]["cloud_functions"] = cloud_functions_result
    
    functions_operational = all(
        func_result["status"] == "operational" 
        for func_result in cloud_functions_result.values()
    )
    if functions_operational:
        test_results["success_count"] += 1
    
    print()
    
    # Test 2: Business Rules Engine
    print("📋 Test 2: Business Rules Engine")
    business_rules_result = test_business_rules()
    test_results["components"]["business_rules"] = business_rules_result
    
    if business_rules_result["status"] == "success":
        test_results["success_count"] += 1
    
    print()
    
    # Test 3: Monitoring System
    print("📊 Test 3: Monitoring System")
    monitoring_result = test_monitoring()
    test_results["components"]["monitoring"] = monitoring_result
    
    if monitoring_result["status"] == "success":
        test_results["success_count"] += 1
    
    print()
    
    # Test 4: Multi-Agent Orchestrator
    print("🤖 Test 4: Multi-Agent Orchestrator")
    orchestrator_result = test_orchestrator()
    test_results["components"]["orchestrator"] = orchestrator_result
    
    if orchestrator_result["status"] == "success":
        test_results["success_count"] += 1
    
    print()
    
    # Calculate overall results
    test_results["test_duration"] = round(time.time() - start_time, 2)
    test_results["success_rate"] = (test_results["success_count"] / test_results["total_tests"]) * 100
    
    if test_results["success_rate"] >= 75:
        test_results["overall_status"] = "operational"
    elif test_results["success_rate"] >= 50:
        test_results["overall_status"] = "partial"
    else:
        test_results["overall_status"] = "degraded"
    
    # Print summary
    print("📋 Test Summary")
    print("-" * 30)
    print(f"Tests passed: {test_results['success_count']}/{test_results['total_tests']}")
    print(f"Success rate: {test_results['success_rate']:.1f}%")
    print(f"Overall status: {test_results['overall_status'].upper()}")
    print(f"Test duration: {test_results['test_duration']} seconds")
    print()
    
    # Component status
    print("🔍 Component Status:")
    for component, result in test_results["components"].items():
        status_icon = "✅" if result.get("status") == "success" or result.get("status") == "operational" else "⚠️" if result.get("status") == "partial" else "❌"
        print(f"  {status_icon} {component.replace('_', ' ').title()}: {result.get('status', 'unknown')}")
    
    print()
    
    # Save results
    with open("comprehensive_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print("💾 Test results saved to comprehensive_test_results.json")
    print()
    
    # Next steps
    print("🚀 Next Steps Based on Results:")
    
    if test_results["overall_status"] == "operational":
        print("✅ System is operational and ready for production use")
        print("1. Configure production API endpoints")
        print("2. Set up monitoring dashboards")
        print("3. Create user authentication")
        print("4. Deploy to production environment")
    elif test_results["overall_status"] == "partial":
        print("⚠️ System is partially operational - some components need attention")
        print("1. Review failed component logs")
        print("2. Fix configuration issues")
        print("3. Re-run tests after fixes")
        print("4. Consider running in limited mode")
    else:
        print("❌ System has significant issues - troubleshooting required")
        print("1. Check all dependencies are installed")
        print("2. Verify GCP authentication and permissions")
        print("3. Check network connectivity")
        print("4. Review error logs for specific issues")
    
    return test_results

def main():
    """Main test function"""
    
    # Run comprehensive test
    results = run_comprehensive_test()
    
    # Exit with appropriate code
    success = results["overall_status"] in ["operational", "partial"]
    exit(0 if success else 1)

if __name__ == "__main__":
    main()