#!/usr/bin/env python3

"""
Phase 3 Testing Suite - Comprehensive testing for advanced features
Tests business rules engine, monitoring system, and production deployment
"""

import time
import logging
from typing import Dict, Any
from datetime import datetime

from business_rules import BusinessRulesEngine, Priority, IssueType, BusinessRuleCategory
from monitoring import MonitoringSystem, MetricType
from orchestrator import MultiAgentOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase3TestSuite:
    """Comprehensive test suite for Phase 3 features"""
    
    def __init__(self):
        self.business_rules = BusinessRulesEngine()
        self.monitoring = MonitoringSystem()
        self.orchestrator = MultiAgentOrchestrator()
        
        self.test_results = {
            "business_rules": {},
            "monitoring": {},
            "production_readiness": {},
            "integration": {}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete Phase 3 test suite"""
        
        logger.info("🚀 Starting Phase 3 Comprehensive Test Suite")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # Test 1: Business Rules Engine
            logger.info("📋 Testing Business Rules Engine...")
            self.test_results["business_rules"] = self._test_business_rules_engine()
            
            # Test 2: Monitoring System
            logger.info("📊 Testing Monitoring System...")
            self.test_results["monitoring"] = self._test_monitoring_system()
            
            # Test 3: Integration Testing
            logger.info("🔗 Testing System Integration...")
            self.test_results["integration"] = self._test_system_integration()
            
            # Test 4: Production Readiness
            logger.info("🏭 Testing Production Readiness...")
            self.test_results["production_readiness"] = self._test_production_readiness()
            
            execution_time = time.time() - start_time
            
            # Generate final report
            final_report = self._generate_test_report(execution_time)
            
            logger.info("✅ Phase 3 Testing Complete!")
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Phase 3 Testing Failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "test_results": self.test_results
            }
    
    def _test_business_rules_engine(self) -> Dict[str, Any]:
        """Test business rules engine functionality"""
        
        results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
        test_cases = [
            {
                "name": "Security Rule Application",
                "ticket_draft": {
                    "summary": "Add user authentication system",
                    "description": "Implement secure login with OAuth integration",
                    "priority": "Medium"
                },
                "expected_rules": ["security_rules"],
                "expected_priority": "High"
            },
            {
                "name": "Performance Rule Application", 
                "ticket_draft": {
                    "summary": "Optimize database query performance",
                    "description": "Improve query execution time and reduce latency",
                    "priority": "Medium"
                },
                "expected_rules": ["performance_rules"],
                "expected_labels": ["performance", "optimization"]
            },
            {
                "name": "Integration Rule Application",
                "ticket_draft": {
                    "summary": "Add external API integration",
                    "description": "Integrate with third-party payment service API",
                    "priority": "Medium"
                },
                "expected_rules": ["integration_rules"],
                "expected_labels": ["integration", "external-dependency"]
            },
            {
                "name": "UI/UX Rule Application",
                "ticket_draft": {
                    "summary": "Redesign user interface",
                    "description": "Update frontend design for better user experience",
                    "priority": "Low"
                },
                "expected_rules": ["ui_ux_rules"],
                "expected_labels": ["ui", "ux", "frontend"]
            }
        ]
        
        for test_case in test_cases:
            try:
                logger.info(f"  Testing: {test_case['name']}")
                
                # Apply business rules
                result = self.business_rules.apply_business_rules(
                    test_case["ticket_draft"], 
                    {}
                )
                
                if not result["success"]:
                    results["tests_failed"] += 1
                    results["test_details"].append({
                        "test": test_case["name"],
                        "status": "failed",
                        "error": "Business rules application failed"
                    })
                    continue
                
                # Verify expected rules were applied
                rules_applied = result["rule_results"]["rules_applied"]
                expected_rules = test_case.get("expected_rules", [])
                
                rules_match = all(rule in rules_applied for rule in expected_rules)
                
                # Verify priority changes if expected
                priority_correct = True
                if "expected_priority" in test_case:
                    priority_correct = result["enhanced_ticket"]["priority"] == test_case["expected_priority"]
                
                # Verify labels if expected
                labels_correct = True
                if "expected_labels" in test_case:
                    ticket_labels = result["enhanced_ticket"].get("labels", [])
                    labels_correct = all(label in ticket_labels for label in test_case["expected_labels"])
                
                if rules_match and priority_correct and labels_correct:
                    results["tests_passed"] += 1
                    results["test_details"].append({
                        "test": test_case["name"],
                        "status": "passed",
                        "rules_applied": rules_applied
                    })
                    logger.info(f"    ✅ {test_case['name']} passed")
                else:
                    results["tests_failed"] += 1
                    results["test_details"].append({
                        "test": test_case["name"],
                        "status": "failed",
                        "error": "Expected behavior not met",
                        "rules_applied": rules_applied,
                        "expected_rules": expected_rules
                    })
                    logger.warning(f"    ❌ {test_case['name']} failed")
                
            except Exception as e:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": test_case["name"],
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"    ❌ {test_case['name']} failed: {str(e)}")
        
        # Test compliance validation
        try:
            logger.info("  Testing: GDPR Compliance Validation")
            
            gdpr_ticket = {
                "summary": "Process user personal data",
                "description": "Collect and store customer email addresses for marketing"
            }
            
            compliance_result = self.business_rules.validate_compliance(gdpr_ticket)
            
            if not compliance_result["compliant"]:
                results["tests_passed"] += 1
                results["test_details"].append({
                    "test": "GDPR Compliance Validation",
                    "status": "passed",
                    "violations_detected": len(compliance_result["violations"])
                })
                logger.info("    ✅ GDPR Compliance Validation passed")
            else:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": "GDPR Compliance Validation",
                    "status": "failed",
                    "error": "Expected GDPR violations not detected"
                })
                logger.warning("    ❌ GDPR Compliance Validation failed")
                
        except Exception as e:
            results["tests_failed"] += 1
            results["test_details"].append({
                "test": "GDPR Compliance Validation",
                "status": "failed",
                "error": str(e)
            })
        
        return results
    
    def _test_monitoring_system(self) -> Dict[str, Any]:
        """Test monitoring system functionality"""
        
        results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
        try:
            # Test workflow monitoring lifecycle
            logger.info("  Testing: Workflow Monitoring Lifecycle")
            
            workflow_id = f"test_workflow_{int(time.time())}"
            
            # Start monitoring
            start_result = self.monitoring.start_workflow_monitoring(
                workflow_id, 
                "Test user request for monitoring"
            )
            
            if start_result["monitoring_started"]:
                logger.info("    ✅ Workflow monitoring started successfully")
                
                # Track agent execution
                self.monitoring.track_agent_execution(
                    workflow_id, "PM Agent", 2.5, True, 0.85, 1
                )
                
                self.monitoring.track_agent_execution(
                    workflow_id, "Tech Lead Agent", 1.8, True, 0.88, 1
                )
                
                self.monitoring.track_agent_execution(
                    workflow_id, "Jira Creator Agent", 1.2, True, None, 1
                )
                
                # Track business rules
                self.monitoring.track_business_rules(
                    workflow_id, ["security_rules", "performance_rules"], 0.5
                )
                
                # Complete monitoring
                completion_result = self.monitoring.complete_workflow_monitoring(
                    workflow_id, True, True, "TEST-123"
                )
                
                if completion_result["monitoring_completed"]:
                    results["tests_passed"] += 1
                    results["test_details"].append({
                        "test": "Workflow Monitoring Lifecycle",
                        "status": "passed",
                        "execution_time": completion_result["total_execution_time"]
                    })
                    logger.info("    ✅ Workflow monitoring lifecycle completed")
                else:
                    results["tests_failed"] += 1
                    results["test_details"].append({
                        "test": "Workflow Monitoring Lifecycle",
                        "status": "failed",
                        "error": "Monitoring completion failed"
                    })
            else:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": "Workflow Monitoring Lifecycle",
                    "status": "failed",
                    "error": "Failed to start monitoring"
                })
            
        except Exception as e:
            results["tests_failed"] += 1
            results["test_details"].append({
                "test": "Workflow Monitoring Lifecycle",
                "status": "failed",
                "error": str(e)
            })
        
        # Test analytics dashboard
        try:
            logger.info("  Testing: Analytics Dashboard Generation")
            
            dashboard = self.monitoring.get_analytics_dashboard(1)  # 1 hour range
            
            if "summary" in dashboard and "agent_performance" in dashboard:
                results["tests_passed"] += 1
                results["test_details"].append({
                    "test": "Analytics Dashboard Generation",
                    "status": "passed",
                    "dashboard_sections": list(dashboard.keys())
                })
                logger.info("    ✅ Analytics dashboard generated successfully")
            else:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": "Analytics Dashboard Generation",
                    "status": "failed",
                    "error": "Dashboard missing required sections"
                })
                
        except Exception as e:
            results["tests_failed"] += 1
            results["test_details"].append({
                "test": "Analytics Dashboard Generation",
                "status": "failed",
                "error": str(e)
            })
        
        return results
    
    def _test_system_integration(self) -> Dict[str, Any]:
        """Test integration between all Phase 3 components"""
        
        results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
        try:
            logger.info("  Testing: Complete System Integration")
            
            # Test full workflow with business rules and monitoring
            test_request = "Add secure user authentication with OAuth integration"
            context = {"priority": "High", "issue_type": "Story"}
            
            # This would normally call the orchestrator, but we'll simulate it
            # since we don't have actual Vertex AI credentials in testing
            workflow_id = f"integration_test_{int(time.time())}"
            
            # Start monitoring
            self.monitoring.start_workflow_monitoring(workflow_id, test_request)
            
            # Simulate PM agent with business rules
            ticket_draft = {
                "summary": "Implement OAuth authentication system",
                "description": "As a user I want secure login so that my account is protected",
                "priority": "Medium",
                "issue_type": "Story"
            }
            
            # Apply business rules
            business_rules_result = self.business_rules.apply_business_rules(
                ticket_draft, context
            )
            
            if business_rules_result["success"]:
                # Track business rules application
                rules_applied = business_rules_result["rule_results"]["rules_applied"]
                self.monitoring.track_business_rules(workflow_id, rules_applied, 0.8)
                
                # Simulate agent executions
                self.monitoring.track_agent_execution(
                    workflow_id, "PM Agent", 3.2, True, 0.82, 1
                )
                
                self.monitoring.track_agent_execution(
                    workflow_id, "Tech Lead Agent", 2.1, True, 0.91, 1
                )
                
                self.monitoring.track_agent_execution(
                    workflow_id, "Jira Creator Agent", 1.4, True, None, 1
                )
                
                # Complete workflow
                completion_result = self.monitoring.complete_workflow_monitoring(
                    workflow_id, True, True, "INT-TEST-001"
                )
                
                # Verify integration success
                if (completion_result["monitoring_completed"] and 
                    "security_rules" in rules_applied and
                    business_rules_result["enhanced_ticket"]["priority"] == "High"):
                    
                    results["tests_passed"] += 1
                    results["test_details"].append({
                        "test": "Complete System Integration",
                        "status": "passed",
                        "workflow_id": workflow_id,
                        "rules_applied": rules_applied,
                        "total_execution_time": completion_result["total_execution_time"]
                    })
                    logger.info("    ✅ System integration test passed")
                else:
                    results["tests_failed"] += 1
                    results["test_details"].append({
                        "test": "Complete System Integration",
                        "status": "failed",
                        "error": "Integration components not working together properly"
                    })
            else:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": "Complete System Integration",
                    "status": "failed",
                    "error": "Business rules application failed"
                })
                
        except Exception as e:
            results["tests_failed"] += 1
            results["test_details"].append({
                "test": "Complete System Integration",
                "status": "failed",
                "error": str(e)
            })
        
        return results
    
    def _test_production_readiness(self) -> Dict[str, Any]:
        """Test production readiness aspects"""
        
        results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
        # Check required files exist
        required_files = [
            "production_server.py",
            "Dockerfile",
            "requirements.txt",
            "business_rules.py",
            "monitoring.py"
        ]
        
        for file_name in required_files:
            try:
                with open(file_name, 'r') as f:
                    content = f.read()
                    if len(content) > 100:  # Basic sanity check
                        results["tests_passed"] += 1
                        results["test_details"].append({
                            "test": f"File: {file_name}",
                            "status": "passed",
                            "size": len(content)
                        })
                        logger.info(f"    ✅ {file_name} exists and has content")
                    else:
                        results["tests_failed"] += 1
                        results["test_details"].append({
                            "test": f"File: {file_name}",
                            "status": "failed",
                            "error": "File too small or empty"
                        })
                        
            except FileNotFoundError:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": f"File: {file_name}",
                    "status": "failed",
                    "error": "File not found"
                })
                logger.warning(f"    ❌ {file_name} not found")
            except Exception as e:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": f"File: {file_name}",
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    def _generate_test_report(self, execution_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_tests_passed = sum(result["tests_passed"] for result in self.test_results.values())
        total_tests_failed = sum(result["tests_failed"] for result in self.test_results.values())
        total_tests = total_tests_passed + total_tests_failed
        
        success_rate = (total_tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "success": total_tests_failed == 0,
            "execution_time": round(execution_time, 2),
            "summary": {
                "total_tests": total_tests,
                "tests_passed": total_tests_passed,
                "tests_failed": total_tests_failed,
                "success_rate_percent": round(success_rate, 2)
            },
            "detailed_results": self.test_results,
            "phase3_readiness": {
                "business_rules_engine": self.test_results["business_rules"]["tests_failed"] == 0,
                "monitoring_system": self.test_results["monitoring"]["tests_failed"] == 0,
                "system_integration": self.test_results["integration"]["tests_failed"] == 0,
                "production_readiness": self.test_results["production_readiness"]["tests_failed"] == 0
            },
            "recommendations": []
        }
        
        # Add recommendations based on results
        if self.test_results["business_rules"]["tests_failed"] > 0:
            report["recommendations"].append("Review business rules engine implementation")
        
        if self.test_results["monitoring"]["tests_failed"] > 0:
            report["recommendations"].append("Fix monitoring system issues before deployment")
        
        if self.test_results["integration"]["tests_failed"] > 0:
            report["recommendations"].append("Resolve system integration problems")
        
        if self.test_results["production_readiness"]["tests_failed"] > 0:
            report["recommendations"].append("Complete production deployment preparation")
        
        if success_rate >= 95:
            report["recommendations"].append("✅ System ready for Phase 3 deployment")
        elif success_rate >= 80:
            report["recommendations"].append("⚠️ Address failing tests before production deployment")
        else:
            report["recommendations"].append("❌ Significant issues detected - postpone deployment")
        
        return report


def main():
    """Run the Phase 3 test suite"""
    print("🚀 PM Jira Agent - Phase 3 Test Suite")
    print("=" * 50)
    
    test_suite = Phase3TestSuite()
    results = test_suite.run_all_tests()
    
    print("\n📋 Test Results Summary")
    print("-" * 30)
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['tests_passed']}")
    print(f"Failed: {results['summary']['tests_failed']}")
    print(f"Success Rate: {results['summary']['success_rate_percent']}%")
    print(f"Execution Time: {results['execution_time']}s")
    
    print("\n🎯 Phase 3 Readiness:")
    readiness = results["phase3_readiness"]
    for component, ready in readiness.items():
        status = "✅" if ready else "❌"
        print(f"  {status} {component.replace('_', ' ').title()}")
    
    print("\n💡 Recommendations:")
    for rec in results["recommendations"]:
        print(f"  • {rec}")
    
    return results["success"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)