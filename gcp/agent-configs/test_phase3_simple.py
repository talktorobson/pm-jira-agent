#!/usr/bin/env python3

"""
Phase 3 Simple Testing Suite - Core logic testing without external dependencies
Tests business rules engine and core functionality
"""

import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplePhase3Tests:
    """Simple test suite for Phase 3 core functionality"""
    
    def __init__(self):
        self.test_results = {
            "business_rules": {},
            "integration": {},
            "production_files": {}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run core Phase 3 tests"""
        
        logger.info("🚀 Starting Phase 3 Simple Test Suite")
        logger.info("=" * 50)
        
        start_time = time.time()
        
        try:
            # Test 1: Business Rules Logic
            logger.info("📋 Testing Business Rules Logic...")
            self.test_results["business_rules"] = self._test_business_rules_logic()
            
            # Test 2: File Structure
            logger.info("📁 Testing Production Files...")
            self.test_results["production_files"] = self._test_production_files()
            
            # Test 3: Integration Logic
            logger.info("🔗 Testing Integration Logic...")
            self.test_results["integration"] = self._test_integration_logic()
            
            execution_time = time.time() - start_time
            
            # Generate final report
            final_report = self._generate_test_report(execution_time)
            
            logger.info("✅ Phase 3 Simple Testing Complete!")
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Phase 3 Testing Failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "test_results": self.test_results
            }
    
    def _test_business_rules_logic(self) -> Dict[str, Any]:
        """Test business rules logic without external dependencies"""
        
        results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
        # Import and test business rules engine
        try:
            from business_rules import BusinessRulesEngine, Priority, IssueType, BusinessRuleCategory
            
            logger.info("  ✅ Business rules module imported successfully")
            
            # Test initialization
            business_rules = BusinessRulesEngine()
            results["tests_passed"] += 1
            results["test_details"].append({
                "test": "Business Rules Engine Initialization",
                "status": "passed"
            })
            
            # Test rule application logic
            test_ticket = {
                "summary": "Add user authentication system",
                "description": "Implement secure login with OAuth integration",
                "priority": "Medium"
            }
            
            rule_result = business_rules.apply_business_rules(test_ticket, {})
            
            if rule_result["success"]:
                results["tests_passed"] += 1
                results["test_details"].append({
                    "test": "Security Rules Application",
                    "status": "passed",
                    "rules_applied": rule_result["rule_results"]["rules_applied"]
                })
                logger.info("  ✅ Security rules applied successfully")
            else:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": "Security Rules Application",
                    "status": "failed",
                    "error": rule_result.get("error")
                })
            
            # Test compliance validation
            compliance_result = business_rules.validate_compliance(test_ticket)
            
            if isinstance(compliance_result, dict) and "compliant" in compliance_result:
                results["tests_passed"] += 1
                results["test_details"].append({
                    "test": "Compliance Validation",
                    "status": "passed",
                    "compliant": compliance_result["compliant"]
                })
                logger.info("  ✅ Compliance validation working")
            else:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": "Compliance Validation",
                    "status": "failed",
                    "error": "Invalid compliance result format"
                })
            
        except ImportError as e:
            results["tests_failed"] += 1
            results["test_details"].append({
                "test": "Business Rules Module Import",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"  ❌ Failed to import business rules: {str(e)}")
        
        except Exception as e:
            results["tests_failed"] += 1
            results["test_details"].append({
                "test": "Business Rules General Test",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"  ❌ Business rules test failed: {str(e)}")
        
        return results
    
    def _test_production_files(self) -> Dict[str, Any]:
        """Test that all required production files exist"""
        
        results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
        required_files = [
            ("production_server.py", "FastAPI production server"),
            ("Dockerfile", "Container deployment configuration"),
            ("requirements.txt", "Python dependencies"),
            ("business_rules.py", "Business rules engine"),
            ("monitoring.py", "Monitoring and analytics"),
            ("orchestrator.py", "Multi-agent orchestrator"),
            ("pm_agent.py", "PM Agent implementation"),
            ("tech_lead_agent.py", "Tech Lead Agent implementation"),
            ("jira_agent.py", "Jira Creator Agent implementation"),
            ("tools.py", "Cloud Function tools"),
            ("../setup-scripts/08-deploy-vertex-agents.sh", "Vertex AI deployment script")
        ]
        
        for file_path, description in required_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                if len(content) > 100:  # Basic sanity check
                    results["tests_passed"] += 1
                    results["test_details"].append({
                        "test": f"File: {file_path}",
                        "status": "passed",
                        "description": description,
                        "size": len(content)
                    })
                    logger.info(f"  ✅ {file_path} exists ({len(content)} chars)")
                else:
                    results["tests_failed"] += 1
                    results["test_details"].append({
                        "test": f"File: {file_path}",
                        "status": "failed",
                        "error": "File too small or empty"
                    })
                    logger.warning(f"  ⚠️ {file_path} is too small")
                    
            except FileNotFoundError:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": f"File: {file_path}",
                    "status": "failed",
                    "error": "File not found"
                })
                logger.error(f"  ❌ {file_path} not found")
                
            except Exception as e:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": f"File: {file_path}",
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"  ❌ Error reading {file_path}: {str(e)}")
        
        return results
    
    def _test_integration_logic(self) -> Dict[str, Any]:
        """Test integration between components"""
        
        results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
        try:
            # Test orchestrator imports
            logger.info("  Testing orchestrator integration...")
            
            with open("orchestrator.py", 'r') as f:
                orchestrator_content = f.read()
            
            # Check for business rules integration
            if "from business_rules import BusinessRulesEngine" in orchestrator_content:
                results["tests_passed"] += 1
                results["test_details"].append({
                    "test": "Business Rules Integration",
                    "status": "passed"
                })
                logger.info("  ✅ Business rules integrated into orchestrator")
            else:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": "Business Rules Integration",
                    "status": "failed",
                    "error": "Business rules not imported in orchestrator"
                })
            
            # Check for business rules usage
            if "_apply_business_rules" in orchestrator_content:
                results["tests_passed"] += 1
                results["test_details"].append({
                    "test": "Business Rules Usage",
                    "status": "passed"
                })
                logger.info("  ✅ Business rules method found in orchestrator")
            else:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": "Business Rules Usage",
                    "status": "failed",
                    "error": "Business rules method not found"
                })
            
            # Test production server integration
            with open("production_server.py", 'r') as f:
                server_content = f.read()
            
            if "from orchestrator import MultiAgentOrchestrator" in server_content:
                results["tests_passed"] += 1
                results["test_details"].append({
                    "test": "Production Server Integration",
                    "status": "passed"
                })
                logger.info("  ✅ Orchestrator integrated into production server")
            else:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": "Production Server Integration",
                    "status": "failed",
                    "error": "Orchestrator not imported in production server"
                })
            
            # Check for FastAPI endpoints
            if "/create-ticket" in server_content and "FastAPI" in server_content:
                results["tests_passed"] += 1
                results["test_details"].append({
                    "test": "API Endpoints",
                    "status": "passed"
                })
                logger.info("  ✅ API endpoints defined in production server")
            else:
                results["tests_failed"] += 1
                results["test_details"].append({
                    "test": "API Endpoints",
                    "status": "failed",
                    "error": "Required API endpoints not found"
                })
            
        except Exception as e:
            results["tests_failed"] += 1
            results["test_details"].append({
                "test": "Integration Logic Test",
                "status": "failed",
                "error": str(e)
            })
            logger.error(f"  ❌ Integration test failed: {str(e)}")
        
        return results
    
    def _generate_test_report(self, execution_time: float) -> Dict[str, Any]:
        """Generate test report"""
        
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
            "phase3_components": {
                "business_rules_engine": self.test_results["business_rules"]["tests_failed"] == 0,
                "production_files": self.test_results["production_files"]["tests_failed"] == 0,
                "system_integration": self.test_results["integration"]["tests_failed"] == 0
            },
            "recommendations": []
        }
        
        # Add recommendations
        if success_rate >= 95:
            report["recommendations"].append("✅ Phase 3 core components ready for deployment")
        elif success_rate >= 80:
            report["recommendations"].append("⚠️ Address failing tests before full deployment")
        else:
            report["recommendations"].append("❌ Critical issues detected - review implementation")
        
        if self.test_results["business_rules"]["tests_failed"] == 0:
            report["recommendations"].append("✅ Business rules engine is functional")
        
        if self.test_results["production_files"]["tests_failed"] == 0:
            report["recommendations"].append("✅ All production files present")
        
        if self.test_results["integration"]["tests_failed"] == 0:
            report["recommendations"].append("✅ Component integration verified")
        
        return report


def main():
    """Run the simple Phase 3 test suite"""
    print("🚀 PM Jira Agent - Phase 3 Simple Test Suite")
    print("=" * 50)
    
    test_suite = SimplePhase3Tests()
    results = test_suite.run_all_tests()
    
    print("\n📋 Test Results Summary")
    print("-" * 30)
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['tests_passed']}")
    print(f"Failed: {results['summary']['tests_failed']}")
    print(f"Success Rate: {results['summary']['success_rate_percent']}%")
    print(f"Execution Time: {results['execution_time']}s")
    
    print("\n🎯 Phase 3 Components:")
    components = results["phase3_components"]
    for component, ready in components.items():
        status = "✅" if ready else "❌"
        print(f"  {status} {component.replace('_', ' ').title()}")
    
    print("\n💡 Recommendations:")
    for rec in results["recommendations"]:
        print(f"  • {rec}")
    
    print("\n🚀 Next Steps:")
    print("  1. Run deployment script: ./08-deploy-vertex-agents.sh")
    print("  2. Configure API Gateway authentication")
    print("  3. Set up monitoring dashboards")
    print("  4. Perform load testing")
    print("  5. Deploy to production environment")
    
    return results["success"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)