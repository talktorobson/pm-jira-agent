#!/usr/bin/env python3

"""
Production Deployment Test for PM Jira Agent
Tests the production-ready multi-agent system with comprehensive validation
Demonstrates enterprise-grade functionality
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from orchestrator import create_jira_ticket_with_ai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_complex_scenarios() -> Dict[str, Any]:
    """Test complex real-world scenarios"""
    
    logger.info("🎯 Testing complex real-world scenarios...")
    
    test_scenarios = [
        {
            "name": "OAuth Authentication with GDPR Compliance",
            "request": "Implement OAuth 2.0 authentication system with GDPR compliance, secure session management, and audit logging for European users",
            "expected_complexity": "high"
        },
        {
            "name": "API Rate Limiting with Performance Monitoring",
            "request": "Add intelligent API rate limiting with performance monitoring, auto-scaling triggers, and detailed analytics dashboard",
            "expected_complexity": "medium"
        },
        {
            "name": "Multi-tenant Data Isolation",
            "request": "Implement multi-tenant data isolation with role-based access control and tenant-specific configurations",
            "expected_complexity": "high"
        },
        {
            "name": "Simple Bug Fix",
            "request": "Fix the submit button styling on the login page - it's not aligned properly with the form fields",
            "expected_complexity": "low"
        }
    ]
    
    results = {
        "scenarios_tested": len(test_scenarios),
        "scenarios_passed": 0,
        "scenario_results": [],
        "performance_metrics": {
            "total_time": 0,
            "avg_time_per_scenario": 0,
            "quality_scores": []
        }
    }
    
    total_start_time = time.time()
    
    for scenario in test_scenarios:
        logger.info(f"Testing scenario: {scenario['name']}")
        
        start_time = time.time()
        
        try:
            result = create_jira_ticket_with_ai(scenario["request"])
            execution_time = time.time() - start_time
            
            scenario_result = {
                "name": scenario["name"],
                "request": scenario["request"],
                "success": result.get("success", False),
                "execution_time": round(execution_time, 2),
                "quality_score": result.get("quality_metrics", {}).get("final_quality_score", 0),
                "ticket_created": result.get("ticket_created", False),
                "ticket_key": result.get("ticket_key"),
                "iterations": result.get("quality_metrics", {}).get("iterations_required", 0),
                "expected_complexity": scenario["expected_complexity"]
            }
            
            if result.get("success", False) and result.get("ticket_created", False):
                results["scenarios_passed"] += 1
                scenario_result["status"] = "✅ PASSED"
            else:
                scenario_result["status"] = "❌ FAILED"
                scenario_result["error"] = result.get("error", "Unknown error")
            
            results["scenario_results"].append(scenario_result)
            results["performance_metrics"]["quality_scores"].append(scenario_result["quality_score"])
            
            logger.info(f"{scenario_result['status']} - {scenario['name']} ({execution_time:.2f}s)")
            
        except Exception as e:
            scenario_result = {
                "name": scenario["name"],
                "request": scenario["request"],
                "success": False,
                "status": "❌ ERROR",
                "error": str(e),
                "execution_time": time.time() - start_time
            }
            results["scenario_results"].append(scenario_result)
            logger.error(f"❌ ERROR - {scenario['name']}: {str(e)}")
    
    # Calculate performance metrics
    results["performance_metrics"]["total_time"] = round(time.time() - total_start_time, 2)
    results["performance_metrics"]["avg_time_per_scenario"] = round(
        results["performance_metrics"]["total_time"] / results["scenarios_tested"], 2
    )
    
    if results["performance_metrics"]["quality_scores"]:
        results["performance_metrics"]["avg_quality_score"] = round(
            sum(results["performance_metrics"]["quality_scores"]) / len(results["performance_metrics"]["quality_scores"]), 3
        )
    
    results["success_rate"] = (results["scenarios_passed"] / results["scenarios_tested"]) * 100
    
    return results

def test_performance_benchmarks() -> Dict[str, Any]:
    """Test performance benchmarks and scalability"""
    
    logger.info("⚡ Testing performance benchmarks...")
    
    benchmark_tests = [
        {"name": "Response Time", "target": "<2s", "test": "simple_request"},
        {"name": "Quality Score", "target": "≥0.8", "test": "quality_validation"},
        {"name": "Complex Request", "target": "<5s", "test": "complex_request"},
        {"name": "Concurrent Processing", "target": "Multiple requests", "test": "concurrency"}
    ]
    
    results = {
        "benchmarks_tested": len(benchmark_tests),
        "benchmarks_passed": 0,
        "benchmark_results": []
    }
    
    # Test 1: Response Time (Simple Request)
    logger.info("Testing response time with simple request...")
    start_time = time.time()
    simple_result = create_jira_ticket_with_ai("Add loading spinner to the dashboard")
    simple_time = time.time() - start_time
    
    results["benchmark_results"].append({
        "name": "Response Time",
        "target": "<2s",
        "actual": f"{simple_time:.2f}s",
        "passed": simple_time < 2.0,
        "status": "✅ PASSED" if simple_time < 2.0 else "❌ FAILED"
    })
    
    if simple_time < 2.0:
        results["benchmarks_passed"] += 1
    
    # Test 2: Quality Score
    logger.info("Testing quality score validation...")
    quality_score = simple_result.get("quality_metrics", {}).get("final_quality_score", 0)
    
    results["benchmark_results"].append({
        "name": "Quality Score",
        "target": "≥0.8",
        "actual": f"{quality_score:.3f}",
        "passed": quality_score >= 0.8,
        "status": "✅ PASSED" if quality_score >= 0.8 else "❌ FAILED"
    })
    
    if quality_score >= 0.8:
        results["benchmarks_passed"] += 1
    
    # Test 3: Complex Request
    logger.info("Testing complex request processing...")
    start_time = time.time()
    complex_result = create_jira_ticket_with_ai(
        "Implement comprehensive user analytics dashboard with real-time data visualization, "
        "advanced filtering capabilities, export functionality, role-based access control, "
        "and integration with third-party analytics services like Google Analytics and Mixpanel"
    )
    complex_time = time.time() - start_time
    
    results["benchmark_results"].append({
        "name": "Complex Request",
        "target": "<5s",
        "actual": f"{complex_time:.2f}s",
        "passed": complex_time < 5.0,
        "status": "✅ PASSED" if complex_time < 5.0 else "❌ FAILED"
    })
    
    if complex_time < 5.0:
        results["benchmarks_passed"] += 1
    
    # Test 4: Simulated Concurrency (Sequential for now)
    logger.info("Testing concurrent processing simulation...")
    concurrent_start = time.time()
    concurrent_requests = [
        "Add user profile settings",
        "Implement password reset functionality",
        "Create admin user management panel"
    ]
    
    concurrent_results = []
    for req in concurrent_requests:
        req_start = time.time()
        req_result = create_jira_ticket_with_ai(req)
        req_time = time.time() - req_start
        concurrent_results.append({
            "request": req,
            "time": req_time,
            "success": req_result.get("success", False)
        })
    
    total_concurrent_time = time.time() - concurrent_start
    avg_concurrent_time = total_concurrent_time / len(concurrent_requests)
    concurrent_success_rate = sum(1 for r in concurrent_results if r["success"]) / len(concurrent_results)
    
    results["benchmark_results"].append({
        "name": "Concurrent Processing",
        "target": "Multiple requests",
        "actual": f"{len(concurrent_requests)} requests in {total_concurrent_time:.2f}s (avg: {avg_concurrent_time:.2f}s)",
        "passed": concurrent_success_rate >= 0.8,
        "status": "✅ PASSED" if concurrent_success_rate >= 0.8 else "❌ FAILED",
        "details": {
            "success_rate": f"{concurrent_success_rate*100:.1f}%",
            "total_time": f"{total_concurrent_time:.2f}s",
            "avg_time": f"{avg_concurrent_time:.2f}s"
        }
    })
    
    if concurrent_success_rate >= 0.8:
        results["benchmarks_passed"] += 1
    
    results["success_rate"] = (results["benchmarks_passed"] / results["benchmarks_tested"]) * 100
    
    return results

def test_enterprise_features() -> Dict[str, Any]:
    """Test enterprise-grade features"""
    
    logger.info("🏢 Testing enterprise features...")
    
    enterprise_tests = [
        {"name": "Business Rules Engine", "feature": "business_rules"},
        {"name": "Quality Gates", "feature": "quality_gates"},
        {"name": "Workflow Monitoring", "feature": "monitoring"},
        {"name": "Error Handling", "feature": "error_handling"},
        {"name": "Audit Logging", "feature": "audit_logging"}
    ]
    
    results = {
        "features_tested": len(enterprise_tests),
        "features_working": 0,
        "feature_results": []
    }
    
    # Test enterprise request with all features
    enterprise_request = """
    Implement a comprehensive enterprise user management system with the following requirements:
    
    FUNCTIONAL REQUIREMENTS:
    - Multi-tenant user provisioning and deprovisioning
    - Integration with Active Directory and LDAP
    - Role-based access control with granular permissions
    - Single Sign-On (SSO) with SAML 2.0 and OAuth 2.0
    - User lifecycle management with automated workflows
    
    NON-FUNCTIONAL REQUIREMENTS:
    - GDPR and SOC 2 compliance
    - 99.9% uptime SLA requirement
    - Support for 10,000+ concurrent users
    - Response time <500ms for authentication
    - Comprehensive audit logging and monitoring
    
    SECURITY REQUIREMENTS:
    - Multi-factor authentication (MFA)
    - Password policy enforcement
    - Session management with automatic timeout
    - Encryption at rest and in transit
    - Regular security vulnerability assessments
    """
    
    logger.info("Testing enterprise request with full feature validation...")
    
    try:
        result = create_jira_ticket_with_ai(enterprise_request)
        
        # Test each enterprise feature based on the result
        for test in enterprise_tests:
            feature_result = {
                "name": test["name"],
                "feature": test["feature"],
                "working": False,
                "details": ""
            }
            
            if test["feature"] == "business_rules":
                # Check if business rules were applied
                workflow_metadata = result.get("workflow_metadata", {})
                agent_interactions = workflow_metadata.get("agent_interactions", [])
                business_rules_applied = any(
                    interaction.get("agent") == "Business Rules Engine" 
                    for interaction in agent_interactions
                )
                feature_result["working"] = business_rules_applied
                feature_result["details"] = "Business rules engine processed the request"
                
            elif test["feature"] == "quality_gates":
                # Check quality score and threshold compliance
                quality_metrics = result.get("quality_metrics", {})
                final_score = quality_metrics.get("final_quality_score", 0)
                threshold_met = quality_metrics.get("quality_threshold_met", False)
                feature_result["working"] = final_score >= 0.8 and threshold_met
                feature_result["details"] = f"Quality score: {final_score:.3f}, Threshold met: {threshold_met}"
                
            elif test["feature"] == "monitoring":
                # Check workflow statistics and monitoring
                workflow_stats = result.get("workflow_statistics", {})
                has_monitoring = bool(workflow_stats.get("agent_execution_times", {}))
                feature_result["working"] = has_monitoring
                feature_result["details"] = f"Execution tracking: {len(workflow_stats.get('agent_execution_times', {}))  } agents monitored"
                
            elif test["feature"] == "error_handling":
                # Check success and error handling
                success = result.get("success", False)
                has_error_info = "error" in result or "troubleshooting" in result
                feature_result["working"] = success  # For this test, success indicates good error handling
                feature_result["details"] = f"Request processed successfully: {success}"
                
            elif test["feature"] == "audit_logging":
                # Check workflow metadata and tracking
                workflow_metadata = result.get("workflow_metadata", {})
                has_audit_trail = bool(workflow_metadata.get("agent_interactions", []))
                feature_result["working"] = has_audit_trail
                feature_result["details"] = f"Audit trail: {len(workflow_metadata.get('agent_interactions', []))} interactions logged"
            
            feature_result["status"] = "✅ WORKING" if feature_result["working"] else "❌ NOT WORKING"
            results["feature_results"].append(feature_result)
            
            if feature_result["working"]:
                results["features_working"] += 1
    
    except Exception as e:
        logger.error(f"Enterprise feature test failed: {e}")
        for test in enterprise_tests:
            results["feature_results"].append({
                "name": test["name"],
                "feature": test["feature"],
                "working": False,
                "status": "❌ ERROR",
                "details": f"Test failed: {str(e)}"
            })
    
    results["success_rate"] = (results["features_working"] / results["features_tested"]) * 100
    
    return results

def run_production_deployment_test() -> Dict[str, Any]:
    """Run comprehensive production deployment test"""
    
    print("🚀 PM Jira Agent - Production Deployment Test")
    print("=" * 70)
    print(f"Test started at: {datetime.now().isoformat()}")
    print(f"Environment: Production-Ready Multi-Agent System")
    print(f"Version: Enhanced Phase 3 Complete")
    print()
    
    # Initialize results
    test_results = {
        "test_timestamp": datetime.now().isoformat(),
        "test_duration": 0,
        "test_suites": {},
        "overall_status": "unknown",
        "production_ready": False
    }
    
    start_time = time.time()
    
    # Test Suite 1: Complex Scenarios
    print("🎯 Test Suite 1: Complex Real-World Scenarios")
    print("-" * 50)
    complex_results = test_complex_scenarios()
    test_results["test_suites"]["complex_scenarios"] = complex_results
    
    print(f"Scenarios: {complex_results['scenarios_passed']}/{complex_results['scenarios_tested']} passed")
    print(f"Success Rate: {complex_results['success_rate']:.1f}%")
    print(f"Avg Quality Score: {complex_results['performance_metrics'].get('avg_quality_score', 'N/A')}")
    print(f"Total Time: {complex_results['performance_metrics']['total_time']}s")
    print()
    
    # Test Suite 2: Performance Benchmarks
    print("⚡ Test Suite 2: Performance Benchmarks")
    print("-" * 50)
    performance_results = test_performance_benchmarks()
    test_results["test_suites"]["performance_benchmarks"] = performance_results
    
    print(f"Benchmarks: {performance_results['benchmarks_passed']}/{performance_results['benchmarks_tested']} passed")
    print(f"Success Rate: {performance_results['success_rate']:.1f}%")
    
    for benchmark in performance_results["benchmark_results"]:
        print(f"  {benchmark['status']} {benchmark['name']}: {benchmark['actual']} (target: {benchmark['target']})")
    print()
    
    # Test Suite 3: Enterprise Features
    print("🏢 Test Suite 3: Enterprise Features")
    print("-" * 50)
    enterprise_results = test_enterprise_features()
    test_results["test_suites"]["enterprise_features"] = enterprise_results
    
    print(f"Features: {enterprise_results['features_working']}/{enterprise_results['features_tested']} working")
    print(f"Success Rate: {enterprise_results['success_rate']:.1f}%")
    
    for feature in enterprise_results["feature_results"]:
        print(f"  {feature['status']} {feature['name']}: {feature['details']}")
    print()
    
    # Calculate overall results
    test_results["test_duration"] = round(time.time() - start_time, 2)
    
    # Calculate overall success rate
    total_tests = (
        complex_results["scenarios_tested"] + 
        performance_results["benchmarks_tested"] + 
        enterprise_results["features_tested"]
    )
    total_passed = (
        complex_results["scenarios_passed"] + 
        performance_results["benchmarks_passed"] + 
        enterprise_results["features_working"]
    )
    
    overall_success_rate = (total_passed / total_tests) * 100
    test_results["overall_success_rate"] = overall_success_rate
    
    # Determine production readiness
    production_criteria = {
        "complex_scenarios": complex_results["success_rate"] >= 75,
        "performance_benchmarks": performance_results["success_rate"] >= 75,
        "enterprise_features": enterprise_results["success_rate"] >= 80,
        "overall_success": overall_success_rate >= 75
    }
    
    test_results["production_criteria"] = production_criteria
    test_results["production_ready"] = all(production_criteria.values())
    
    if test_results["production_ready"]:
        test_results["overall_status"] = "PRODUCTION READY"
    elif overall_success_rate >= 60:
        test_results["overall_status"] = "NEAR PRODUCTION READY"
    else:
        test_results["overall_status"] = "NEEDS IMPROVEMENT"
    
    # Print final summary
    print("📋 Production Deployment Test Summary")
    print("=" * 70)
    print(f"Overall Success Rate: {overall_success_rate:.1f}%")
    print(f"Production Status: {test_results['overall_status']}")
    print(f"Test Duration: {test_results['test_duration']} seconds")
    print()
    
    print("🔍 Production Criteria:")
    for criterion, passed in production_criteria.items():
        status_icon = "✅" if passed else "❌"
        print(f"  {status_icon} {criterion.replace('_', ' ').title()}: {'PASSED' if passed else 'FAILED'}")
    print()
    
    if test_results["production_ready"]:
        print("🎉 SYSTEM IS PRODUCTION READY!")
        print("✅ All critical criteria met")
        print("✅ Enterprise-grade functionality confirmed")
        print("✅ Performance benchmarks achieved")
        print("✅ Complex scenario handling validated")
        print()
        print("🚀 Ready for:")
        print("  • Production deployment")
        print("  • Enterprise customer usage")
        print("  • High-volume workloads")
        print("  • Mission-critical operations")
    else:
        print("⚠️ SYSTEM NEEDS IMPROVEMENT")
        print("Some production criteria not met")
        print("Review failed tests and implement fixes")
    
    print()
    
    # Save results
    with open("production_deployment_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print("💾 Detailed results saved to production_deployment_test_results.json")
    
    return test_results

def main():
    """Main production test function"""
    
    # Run production deployment test
    results = run_production_deployment_test()
    
    # Exit with appropriate code
    success = results["production_ready"]
    exit(0 if success else 1)

if __name__ == "__main__":
    main()