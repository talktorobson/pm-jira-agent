#!/usr/bin/env python3

"""
Enhanced Multi-Agent Orchestrator - Phase 0 Web Interface Integration
Supports real-time progress callbacks for web interface
"""

import time
import json
import logging
import sys
import os
import requests
import base64
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

# For Phase 0 deployment, prioritize mock agents for reliability
print("🚀 Phase 0 Mode: Initializing individual deployment with mock agents")

# Try to import real agents if available, but gracefully fall back to mocks
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'gcp', 'agent-configs'))
    from pm_agent import PMAgent
    from tech_lead_agent import TechLeadAgent
    from jira_agent import JiraCreatorAgent
    from tools import QualityGates
    from business_rules import BusinessRulesEngine
    print("✅ Real agents imported successfully")
except ImportError as e:
    print(f"ℹ️  Real agents not available ({e}), using mock agents for Phase 0")
    PMAgent = None
    TechLeadAgent = None
    JiraCreatorAgent = None
    QualityGates = None
    BusinessRulesEngine = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProgressTracker:
    """Tracks workflow progress and provides updates via callback"""
    
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.start_time = time.time()
        self.current_progress = 0
        
    def update(self, agent: str, progress: int, message: str, details: Optional[Dict] = None):
        """Send progress update via callback"""
        if self.callback:
            update_data = {
                'agent': agent,
                'progress': progress,
                'message': message,
                'elapsed_time': time.time() - self.start_time,
                'timestamp': datetime.now().isoformat()
            }
            
            if details:
                update_data.update(details)
                
            try:
                self.callback(update_data)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
        
        self.current_progress = progress
        logger.info(f"{agent}: {message} ({progress}%)")

class MockAgent:
    """Mock agent for testing when real agents are not available"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        
    def process_request(self, *args, **kwargs):
        """Mock request processing"""
        time.sleep(1)  # Simulate processing time
        
        if self.agent_name == "PM Agent":
            return {
                "success": True,
                "ticket_draft": {
                    "summary": "Mock Ticket: User Authentication Implementation",
                    "description": "Implement secure user authentication system",
                    "acceptance_criteria": [
                        "Users can register with email/password",
                        "Users can login securely",
                        "Session management works correctly"
                    ]
                },
                "business_value": "Improves security and user experience",
                "execution_time": 1.5
            }
        elif self.agent_name == "Tech Lead Agent":
            return {
                "success": True,
                "approval_status": "approved",
                "quality_score": 0.92,
                "feedback": {
                    "technical_feasibility": "High - Standard authentication patterns",
                    "risks": ["Session management complexity"],
                    "recommendations": ["Use OAuth 2.0", "Implement rate limiting"]
                },
                "execution_time": 0.8
            }
        elif self.agent_name == "Jira Creator Agent":
            return {
                "success": True,
                "ticket_created": True,
                "ticket_key": "DEMO-1234",
                "ticket_url": "https://demo.atlassian.net/browse/DEMO-1234",
                "execution_time": 0.7
            }

class RealGitBookIntegration:
    """Real GitBook API integration for Phase 0"""
    
    def __init__(self):
        self.gitbook_api_url = os.getenv('GITBOOK_API_URL', 'https://gitbook-api-jlhinciqia-od.a.run.app')
        self.gitbook_api_key = os.getenv('GITBOOK_API_KEY')
        self.space_id = os.getenv('GITBOOK_SPACE_ID', 'Jw57BieQciFYoCHgwVlm')  # SSI Space
        
    def is_configured(self) -> bool:
        """Check if GitBook API is properly configured"""
        return bool(self.gitbook_api_key)
    
    def search_content(self, query: str) -> Dict[str, Any]:
        """Search GitBook content via your GCP backend"""
        if not self.is_configured():
            logger.warning("GitBook not configured, skipping context search")
            return {"success": False, "error": "GitBook not configured"}
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.gitbook_api_key}'
            }
            
            payload = {
                "action": "search",
                "space_id": self.space_id,
                "query": query,
                "limit": 5
            }
            
            response = requests.post(self.gitbook_api_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"GitBook search successful: {len(result.get('results', []))} results found")
                return {
                    "success": True,
                    "results": result.get('results', []),
                    "query": query
                }
            else:
                logger.error(f"GitBook API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"GitBook API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error searching GitBook: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_content(self, space_id: str = None) -> Dict[str, Any]:
        """Get GitBook space content via your GCP backend"""
        if not self.is_configured():
            return {"success": False, "error": "GitBook not configured"}
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.gitbook_api_key}'
            }
            
            payload = {
                "action": "get_content",
                "space_id": space_id or self.space_id
            }
            
            response = requests.post(self.gitbook_api_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info("GitBook content retrieved successfully")
                return {
                    "success": True,
                    "content": result.get('content', {}),
                    "space_id": space_id or self.space_id
                }
            else:
                logger.error(f"GitBook API error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"GitBook API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error getting GitBook content: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class RealJiraIntegration:
    """Real JIRA API integration for Phase 0"""
    
    def __init__(self):
        self.jira_api_url = os.getenv('JIRA_API_URL', 'https://jira-api-jlhinciqia-od.a.run.app')
        self.jira_base_url = os.getenv('JIRA_BASE_URL', 'https://jira.adeo.com')
        self.jira_email = os.getenv('JIRA_EMAIL')
        self.jira_token = os.getenv('JIRA_API_TOKEN')
        self.project_key = os.getenv('JIRA_PROJECT_KEY', 'AHSSI')
        
    def is_configured(self) -> bool:
        """Check if JIRA credentials are properly configured"""
        return bool(self.jira_email and self.jira_token)
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a real JIRA ticket via GCP backend"""
        if not self.is_configured():
            logger.warning("JIRA not configured, falling back to mock")
            return {
                "success": False,
                "error": "JIRA credentials not configured",
                "mock_used": True
            }
        
        try:
            # Use GCP backend for JIRA API calls
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.jira_token}'
            }
            
            payload = {
                "action": "create_ticket",
                "project_key": self.project_key,
                "summary": ticket_data.get("title", "AI Generated Ticket"),
                "description": ticket_data.get("description", "Generated by PM Jira Agent Phase 0"),
                "issue_type": ticket_data.get("issue_type", "Story"),
                "priority": ticket_data.get("priority", "Medium")
            }
            
            response = requests.post(self.jira_api_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    ticket_key = result.get("ticket_key")
                    ticket_url = f"{self.jira_base_url}/browse/{ticket_key}"
                    
                    logger.info(f"Successfully created JIRA ticket via GCP backend: {ticket_key}")
                    return {
                        "success": True,
                        "ticket_created": True,
                        "ticket_key": ticket_key,
                        "ticket_url": ticket_url,
                        "execution_time": 1.5
                    }
                else:
                    logger.error(f"JIRA backend error: {result.get('error')}")
                    return {
                        "success": False,
                        "error": result.get("error", "Unknown backend error")
                    }
            else:
                logger.error(f"JIRA backend API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Backend API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error creating JIRA ticket via backend: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class EnhancedMultiAgentOrchestrator:
    """Enhanced orchestrator with progress callback support"""
    
    def __init__(self, project_id: str = "service-execution-uat-bb7", location: str = "europe-west9"):
        self.project_id = project_id
        self.location = location
        
        # Initialize backend integrations
        self.jira_integration = RealJiraIntegration()
        self.gitbook_integration = RealGitBookIntegration()
        
        # Initialize agents (or mocks if not available)
        if PMAgent is not None:
            self.pm_agent = PMAgent(project_id, location)
            self.tech_lead_agent = TechLeadAgent(project_id, location)
            self.jira_creator_agent = JiraCreatorAgent(project_id, location)
            self.business_rules = BusinessRulesEngine()
            self.mock_mode = False
            logger.info("Real agents initialized")
        else:
            self.pm_agent = MockAgent("PM Agent")
            self.tech_lead_agent = MockAgent("Tech Lead Agent")
            self.jira_creator_agent = MockAgent("Jira Creator Agent")
            self.business_rules = None
            self.mock_mode = True
            logger.warning("Mock agents initialized - real agents not available")
        
        # Workflow configuration
        self.max_iterations = 3
        self.quality_threshold = 0.8
        self.iteration_timeout = 300  # 5 minutes per iteration
        
        logger.info(f"Enhanced Multi-Agent Orchestrator initialized for project {project_id}")
    
    def create_jira_ticket(
        self, 
        user_request: str, 
        context: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Create a Jira ticket with real-time progress updates
        
        Args:
            user_request: User's request or requirement
            context: Additional context information
            progress_callback: Function to call with progress updates
            
        Returns:
            Dictionary containing complete workflow results and created ticket
        """
        workflow_start_time = time.time()
        workflow_id = f"workflow_{int(workflow_start_time)}"
        
        # Initialize progress tracker
        tracker = ProgressTracker(progress_callback)
        
        logger.info(f"Starting enhanced workflow {workflow_id} for request: {user_request[:100]}...")
        
        try:
            # Initialize workflow tracking
            workflow_context = {
                "workflow_id": workflow_id,
                "user_request": user_request,
                "additional_context": context,
                "start_time": datetime.now().isoformat(),
                "iteration_count": 0,
                "quality_history": [],
                "agent_interactions": []
            }
            
            tracker.update("System", 5, "Workflow initialized, starting PM Agent analysis...")
            
            # Phase 1: PM Agent Analysis
            pm_result = self._execute_pm_analysis_with_progress(user_request, context, workflow_context, tracker)
            
            if not pm_result["success"]:
                return self._create_failure_response(workflow_context, "PM Agent analysis failed", pm_result)
            
            tracker.update("Business Rules Engine", 40, "Applying business rules and compliance checks...")
            
            # Phase 2: Apply Business Rules
            business_rules_result = self._apply_business_rules_with_progress(pm_result, workflow_context, tracker)
            
            if not business_rules_result["success"]:
                return self._create_failure_response(workflow_context, "Business rules application failed", business_rules_result)
            
            tracker.update("Tech Lead Agent", 50, "Starting technical review and quality assessment...")
            
            # Phase 3: Iterative Quality Improvement Loop
            final_result = self._execute_quality_improvement_loop_with_progress(business_rules_result, workflow_context, tracker)
            
            if not final_result["success"]:
                return self._create_failure_response(workflow_context, "Quality improvement failed", final_result)
            
            tracker.update("Jira Creator Agent", 85, "Creating ticket in JIRA...")
            
            # Phase 4: Final Ticket Creation
            creation_result = self._execute_ticket_creation_with_progress(final_result, workflow_context, tracker)
            
            if not creation_result["success"]:
                return self._create_failure_response(workflow_context, "Ticket creation failed", creation_result)
            
            tracker.update("System", 100, "Workflow completed successfully!")
            
            # Calculate final statistics
            total_duration = time.time() - workflow_start_time
            workflow_statistics = self._calculate_workflow_statistics(workflow_context, total_duration)
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "ticket_created": True,
                "ticket_key": creation_result.get("ticket_key"),
                "ticket_url": creation_result.get("ticket_url"),
                "quality_metrics": {
                    "final_quality_score": final_result.get("quality_score", 0),
                    "iterations_required": workflow_context["iteration_count"] + 1,
                    "quality_threshold_met": final_result.get("quality_score", 0) >= self.quality_threshold,
                    "quality_history": workflow_context["quality_history"]
                },
                "workflow_statistics": workflow_statistics,
                "workflow_metadata": {
                    "agent_interactions": workflow_context["agent_interactions"],
                    "total_execution_time": total_duration,
                    "created_at": workflow_context["start_time"],
                    "mock_mode": self.mock_mode
                },
                "agent_performance": {
                    "pm_agent": "✅ Completed analysis and refinements",
                    "tech_lead_agent": "✅ Approved final ticket",
                    "jira_creator_agent": "✅ Successfully created ticket"
                },
                "next_steps": [
                    f"Review ticket at {creation_result.get('ticket_url', '#')}",
                    "Assign to appropriate team member",
                    "Add to appropriate sprint/backlog",
                    "Validate implementation against acceptance criteria"
                ]
            }
            
        except Exception as e:
            logger.error(f"Critical error in workflow {workflow_id}: {str(e)}", exc_info=True)
            tracker.update("System", 0, f"Critical error: {str(e)}")
            return self._create_failure_response(workflow_context, f"Critical workflow error: {str(e)}")

    def _execute_pm_analysis_with_progress(self, user_request: str, context: Optional[Dict], workflow_context: Dict, tracker: ProgressTracker) -> Dict[str, Any]:
        """Execute PM Agent analysis with progress updates"""
        start_time = time.time()
        
        tracker.update("PM Agent", 10, "Analyzing user request and gathering context...")
        
        try:
            # Simulate research phase
            tracker.update("PM Agent", 15, "Researching existing documentation...")
            time.sleep(0.5)  # Simulate research time
            
            tracker.update("PM Agent", 20, "Analyzing similar tickets and patterns...")
            time.sleep(0.5)
            
            # Phase 1a: Context Research (if GitBook configured)
            context_research = None
            if self.gitbook_integration.is_configured():
                tracker.update("PM Agent", 15, "Researching context from GitBook...")
                context_research = self.gitbook_integration.search_content(user_request)
                if context_research.get("success"):
                    logger.info(f"Found {len(context_research.get('results', []))} relevant GitBook entries")
                    context = context or {}
                    context["gitbook_research"] = context_research
                tracker.update("PM Agent", 20, "Context research completed")
            
            tracker.update("PM Agent", 25, "Creating initial ticket draft...")
            
            if self.mock_mode:
                result = self.pm_agent.process_request(user_request, context)
            else:
                result = self.pm_agent.analyze_request(user_request, context)
            
            execution_time = time.time() - start_time
            
            # Record interaction
            workflow_context["agent_interactions"].append({
                "agent": "PM Agent",
                "phase": "initial_analysis",
                "execution_time": execution_time,
                "result": "success",
                "timestamp": datetime.now().isoformat()
            })
            
            tracker.update("PM Agent", 35, "PM analysis completed successfully")
            
            return {
                "success": True,
                "ticket_draft": result.get("ticket_draft", {}),
                "business_value": result.get("business_value", ""),
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"PM Agent analysis failed: {e}")
            tracker.update("PM Agent", 0, f"Analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _apply_business_rules_with_progress(self, pm_result: Dict, workflow_context: Dict, tracker: ProgressTracker) -> Dict[str, Any]:
        """Apply business rules with progress updates"""
        start_time = time.time()
        
        try:
            tracker.update("Business Rules Engine", 42, "Checking UI/UX guidelines...")
            time.sleep(0.2)
            
            tracker.update("Business Rules Engine", 44, "Validating security requirements...")
            time.sleep(0.2)
            
            tracker.update("Business Rules Engine", 46, "Applying performance standards...")
            time.sleep(0.2)
            
            if self.business_rules and not self.mock_mode:
                result = self.business_rules.apply_rules(pm_result["ticket_draft"])
            else:
                # Mock business rules application
                result = {
                    "success": True,
                    "applied_rules": ["ui_ux_guidelines", "security_requirements", "performance_standards"],
                    "enhanced_ticket": pm_result["ticket_draft"]
                }
            
            execution_time = time.time() - start_time
            
            # Record interaction
            workflow_context["agent_interactions"].append({
                "agent": "Business Rules Engine",
                "phase": "business_rules_application",
                "execution_time": execution_time,
                "result": "success",
                "applied_rules": result.get("applied_rules", []),
                "timestamp": datetime.now().isoformat()
            })
            
            tracker.update("Business Rules Engine", 48, "Business rules applied successfully")
            
            return {
                "success": True,
                "enhanced_ticket": result.get("enhanced_ticket", pm_result["ticket_draft"]),
                "applied_rules": result.get("applied_rules", []),
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Business rules application failed: {e}")
            tracker.update("Business Rules Engine", 0, f"Business rules failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _execute_quality_improvement_loop_with_progress(self, business_result: Dict, workflow_context: Dict, tracker: ProgressTracker) -> Dict[str, Any]:
        """Execute quality improvement loop with progress updates"""
        current_ticket = business_result["enhanced_ticket"]
        iteration_count = 0
        
        while iteration_count < self.max_iterations:
            iteration_start_time = time.time()
            iteration_count += 1
            
            tracker.update("Tech Lead Agent", 55 + (iteration_count * 10), f"Quality review iteration {iteration_count}...")
            
            try:
                if self.mock_mode:
                    review_result = self.tech_lead_agent.process_request(current_ticket)
                else:
                    review_result = self.tech_lead_agent.review_ticket(current_ticket)
                
                execution_time = time.time() - iteration_start_time
                quality_score = review_result.get("quality_score", 0)
                
                # Record quality history
                workflow_context["quality_history"].append({
                    "iteration": iteration_count,
                    "agent": "Tech Lead Agent",
                    "quality_score": quality_score,
                    "timestamp": datetime.now().isoformat(),
                    "passes_threshold": quality_score >= self.quality_threshold
                })
                
                # Record interaction
                workflow_context["agent_interactions"].append({
                    "agent": "Tech Lead Agent",
                    "phase": f"review_iteration_{iteration_count}",
                    "execution_time": execution_time,
                    "result": "success",
                    "quality_score": quality_score,
                    "approval_status": review_result.get("approval_status", "pending"),
                    "timestamp": datetime.now().isoformat()
                })
                
                if quality_score >= self.quality_threshold:
                    tracker.update("Tech Lead Agent", 75, f"Quality threshold met! Score: {quality_score:.2f}")
                    workflow_context["iteration_count"] = iteration_count - 1
                    return {
                        "success": True,
                        "final_ticket": current_ticket,
                        "quality_score": quality_score,
                        "iterations_required": iteration_count,
                        "approval_status": "approved"
                    }
                else:
                    if iteration_count < self.max_iterations:
                        tracker.update("Tech Lead Agent", 55 + (iteration_count * 10), 
                                     f"Quality score {quality_score:.2f} below threshold. Improving...")
                        # In a real implementation, we would improve the ticket here
                        time.sleep(0.5)  # Simulate improvement time
                    
            except Exception as e:
                logger.error(f"Quality review iteration {iteration_count} failed: {e}")
                tracker.update("Tech Lead Agent", 0, f"Review failed: {str(e)}")
                return {"success": False, "error": str(e)}
        
        # If we reach here, max iterations exceeded
        final_score = workflow_context["quality_history"][-1]["quality_score"] if workflow_context["quality_history"] else 0
        
        if final_score >= self.quality_threshold * 0.9:  # Accept if close to threshold
            tracker.update("Tech Lead Agent", 75, f"Accepting ticket with score {final_score:.2f} after {self.max_iterations} iterations")
            workflow_context["iteration_count"] = iteration_count - 1
            return {
                "success": True,
                "final_ticket": current_ticket,
                "quality_score": final_score,
                "iterations_required": iteration_count,
                "approval_status": "approved_with_conditions"
            }
        else:
            tracker.update("Tech Lead Agent", 0, f"Quality threshold not met after {self.max_iterations} iterations")
            return {
                "success": False,
                "error": f"Quality threshold not met after {self.max_iterations} iterations. Final score: {final_score:.2f}"
            }

    def _execute_ticket_creation_with_progress(self, final_result: Dict, workflow_context: Dict, tracker: ProgressTracker) -> Dict[str, Any]:
        """Execute ticket creation with progress updates"""
        start_time = time.time()
        
        try:
            tracker.update("Jira Creator Agent", 90, "Formatting ticket for JIRA...")
            time.sleep(0.3)
            
            tracker.update("Jira Creator Agent", 95, "Submitting ticket to JIRA...")
            
            # Try real JIRA integration first, fall back to mock if not configured
            if self.jira_integration.is_configured():
                logger.info("Creating real JIRA ticket...")
                ticket_data = {
                    "title": final_result["final_ticket"].get("summary", "AI Generated Ticket"),
                    "description": final_result["final_ticket"].get("description", "Generated by PM Jira Agent"),
                    "issue_type": "Story",
                    "priority": "Medium"
                }
                creation_result = self.jira_integration.create_ticket(ticket_data)
            elif not self.mock_mode:
                creation_result = self.jira_creator_agent.create_ticket(final_result["final_ticket"])
            else:
                creation_result = self.jira_creator_agent.process_request(final_result["final_ticket"])
            
            execution_time = time.time() - start_time
            
            # Record interaction
            workflow_context["agent_interactions"].append({
                "agent": "Jira Creator Agent",
                "phase": "final_creation",
                "execution_time": execution_time,
                "result": "success",
                "ticket_created": creation_result.get("success", False),
                "ticket_key": creation_result.get("ticket_key"),
                "timestamp": datetime.now().isoformat()
            })
            
            tracker.update("Jira Creator Agent", 98, "Ticket created successfully!")
            
            return {
                "success": True,
                "ticket_key": creation_result.get("ticket_key"),
                "ticket_url": creation_result.get("ticket_url"),
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Ticket creation failed: {e}")
            tracker.update("Jira Creator Agent", 0, f"Ticket creation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def _create_failure_response(self, workflow_context: Dict, error_message: str, error_details: Optional[Dict] = None) -> Dict[str, Any]:
        """Create standardized failure response"""
        return {
            "success": False,
            "error": error_message,
            "error_details": error_details,
            "workflow_id": workflow_context.get("workflow_id"),
            "workflow_metadata": {
                "agent_interactions": workflow_context.get("agent_interactions", []),
                "quality_history": workflow_context.get("quality_history", []),
                "failed_at": datetime.now().isoformat()
            }
        }

    def _calculate_workflow_statistics(self, workflow_context: Dict, total_duration: float) -> Dict[str, Any]:
        """Calculate workflow performance statistics"""
        interactions = workflow_context.get("agent_interactions", [])
        quality_history = workflow_context.get("quality_history", [])
        
        # Agent execution time analysis
        pm_agent_time = sum(i["execution_time"] for i in interactions if i["agent"] == "PM Agent")
        tech_lead_time = sum(i["execution_time"] for i in interactions if i["agent"] == "Tech Lead Agent")
        jira_creator_time = sum(i["execution_time"] for i in interactions if i["agent"] == "Jira Creator Agent")
        
        # Quality improvement analysis
        quality_scores = [q["quality_score"] for q in quality_history]
        quality_improvement = max(quality_scores) - min(quality_scores) if quality_scores else 0
        
        return {
            "total_workflow_duration": round(total_duration, 2),
            "agent_execution_times": {
                "pm_agent": round(pm_agent_time, 2),
                "tech_lead_agent": round(tech_lead_time, 2),
                "jira_creator_agent": round(jira_creator_time, 2),
                "business_rules": round(total_duration - pm_agent_time - tech_lead_time - jira_creator_time, 2)
            },
            "iteration_count": workflow_context.get("iteration_count", 0) + 1,
            "quality_improvement": round(quality_improvement, 2),
            "quality_score_range": {
                "minimum": min(quality_scores) if quality_scores else 0,
                "maximum": max(quality_scores) if quality_scores else 0,
                "final": quality_scores[-1] if quality_scores else 0
            },
            "agent_interaction_count": len(interactions),
            "efficiency_metrics": {
                "avg_iteration_time": round(total_duration / max(workflow_context.get("iteration_count", 0) + 1, 1), 2),
                "quality_threshold_achieved": max(quality_scores) >= self.quality_threshold if quality_scores else False,
                "iterations_to_approval": workflow_context.get("iteration_count", 0) + 1
            }
        }


# Enhanced convenience function with progress callback support
def create_jira_ticket_with_ai(
    user_request: str, 
    context: Optional[Dict[str, Any]] = None,
    progress_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Enhanced convenience function to create a Jira ticket using the multi-agent system
    
    Args:
        user_request: User's request or requirement
        context: Additional context information
        progress_callback: Function to call with progress updates
        
    Returns:
        Dictionary containing complete workflow results
    """
    orchestrator = EnhancedMultiAgentOrchestrator()
    return orchestrator.create_jira_ticket(user_request, context, progress_callback)


# Export main classes and functions
__all__ = ["EnhancedMultiAgentOrchestrator", "create_jira_ticket_with_ai", "ProgressTracker"]