#!/usr/bin/env python3

"""
Multi-Agent Orchestrator - Coordinating PM Jira Agent Workflow
Orchestrates the workflow between PM Agent, Tech Lead Agent, and Jira Creator Agent
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from pm_agent import PMAgent
from tech_lead_agent import TechLeadAgent
from jira_agent import JiraCreatorAgent
from tools import QualityGates
from business_rules import BusinessRulesEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiAgentOrchestrator:
    """Orchestrates multi-agent workflow for creating high-quality Jira tickets"""
    
    def __init__(self, project_id: str = "service-execution-uat-bb7", location: str = "europe-west9"):
        self.project_id = project_id
        self.location = location
        
        # Initialize agents
        self.pm_agent = PMAgent(project_id, location)
        self.tech_lead_agent = TechLeadAgent(project_id, location)
        self.jira_creator_agent = JiraCreatorAgent(project_id, location)
        
        # Initialize business rules engine
        self.business_rules = BusinessRulesEngine()
        
        # Workflow configuration
        self.max_iterations = 3
        self.quality_threshold = 0.8
        self.iteration_timeout = 300  # 5 minutes per iteration
        
        logger.info(f"Multi-Agent Orchestrator initialized for project {project_id}")
    
    def create_jira_ticket(self, user_request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for creating a Jira ticket through multi-agent workflow
        
        Args:
            user_request: User's request or requirement
            context: Additional context information
            
        Returns:
            Dictionary containing complete workflow results and created ticket
        """
        workflow_start_time = time.time()
        workflow_id = f"workflow_{int(workflow_start_time)}"
        
        logger.info(f"Starting multi-agent workflow {workflow_id} for request: {user_request[:100]}...")
        
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
            
            # Phase 1: PM Agent Analysis
            pm_result = self._execute_pm_analysis(user_request, context, workflow_context)
            
            if not pm_result["success"]:
                return self._create_failure_response(workflow_context, "PM Agent analysis failed", pm_result)
            
            # Phase 2: Apply Business Rules
            business_rules_result = self._apply_business_rules(pm_result, workflow_context)
            
            if not business_rules_result["success"]:
                return self._create_failure_response(workflow_context, "Business rules application failed", business_rules_result)
            
            # Phase 3: Iterative Quality Improvement Loop
            final_result = self._execute_quality_improvement_loop(business_rules_result, workflow_context)
            
            if not final_result["success"]:
                return self._create_failure_response(workflow_context, "Quality improvement failed", final_result)
            
            # Phase 4: Final Ticket Creation
            creation_result = self._execute_ticket_creation(final_result, workflow_context)
            
            # Finalize workflow
            workflow_duration = time.time() - workflow_start_time
            return self._create_success_response(creation_result, workflow_context, workflow_duration)
            
        except Exception as e:
            logger.error(f"Orchestrator error in workflow {workflow_id}: {str(e)}")
            return self._create_failure_response(workflow_context, "Orchestrator error", {"error": str(e)})
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get status of a running or completed workflow
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Dictionary containing workflow status and progress
        """
        # In a real implementation, this would query a workflow state store
        return {
            "workflow_id": workflow_id,
            "status": "completed",  # placeholder
            "message": "Workflow status tracking not implemented in this version"
        }
    
    def _execute_pm_analysis(self, user_request: str, context: Optional[Dict[str, Any]], workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PM Agent analysis phase"""
        
        logger.info("Phase 1: PM Agent Analysis")
        
        start_time = time.time()
        pm_result = self.pm_agent.analyze_user_request(user_request, context)
        execution_time = time.time() - start_time
        
        # Track interaction
        workflow_context["agent_interactions"].append({
            "agent": "PM Agent",
            "phase": "initial_analysis",
            "execution_time": execution_time,
            "result": "success" if pm_result["success"] else "failure",
            "quality_score": pm_result.get("quality_assessment", {}).get("overall_score", 0)
        })
        
        if pm_result["success"]:
            # Track quality history
            workflow_context["quality_history"].append({
                "iteration": 1,
                "agent": "PM Agent",
                "quality_score": pm_result["quality_assessment"]["overall_score"],
                "passes_threshold": pm_result["quality_assessment"]["passes_quality_gate"]
            })
        
        return pm_result
    
    def _apply_business_rules(self, pm_result: Dict[str, Any], workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules to enhance ticket draft"""
        
        logger.info("Phase 2: Applying Business Rules")
        
        start_time = time.time()
        ticket_draft = pm_result["ticket_draft"]
        context = workflow_context.get("additional_context", {})
        
        # Apply business rules
        business_rules_result = self.business_rules.apply_business_rules(ticket_draft, context)
        execution_time = time.time() - start_time
        
        # Track interaction
        workflow_context["agent_interactions"].append({
            "agent": "Business Rules Engine",
            "phase": "business_rules_application",
            "execution_time": execution_time,
            "result": "success" if business_rules_result["success"] else "failure",
            "rules_applied": business_rules_result.get("rule_results", {}).get("rules_applied", [])
        })
        
        if business_rules_result["success"]:
            # Update pm_result with enhanced ticket
            enhanced_result = pm_result.copy()
            enhanced_result["ticket_draft"] = business_rules_result["enhanced_ticket"]
            enhanced_result["business_rules_applied"] = business_rules_result["rule_results"]
            enhanced_result["compliance_validation"] = self.business_rules.validate_compliance(
                business_rules_result["enhanced_ticket"]
            )
            
            logger.info(f"Business rules applied successfully: {business_rules_result.get('rule_results', {}).get('rules_applied', [])}")
            return enhanced_result
        else:
            logger.error(f"Business rules application failed: {business_rules_result.get('error')}")
            return business_rules_result
    
    def _execute_quality_improvement_loop(self, business_rules_result: Dict[str, Any], workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute iterative quality improvement loop between PM and Tech Lead agents"""
        
        logger.info("Phase 3: Quality Improvement Loop")
        
        current_ticket_draft = business_rules_result["ticket_draft"]
        current_pm_analysis = business_rules_result
        iteration = 1
        
        while iteration <= self.max_iterations:
            workflow_context["iteration_count"] = iteration
            logger.info(f"Quality improvement iteration {iteration}/{self.max_iterations}")
            
            # Tech Lead Review
            tech_lead_result = self._execute_tech_lead_review(current_ticket_draft, current_pm_analysis, workflow_context, iteration)
            
            if not tech_lead_result["success"]:
                return tech_lead_result
            
            # Check if approved
            if tech_lead_result["approval_status"] == "approved":
                logger.info(f"Ticket approved by Tech Lead on iteration {iteration}")
                return {
                    "success": True,
                    "final_ticket_draft": current_ticket_draft,
                    "final_quality_score": tech_lead_result["quality_score"],
                    "tech_lead_approval": True,
                    "iterations_completed": iteration,
                    "workflow_context": workflow_context
                }
            
            # If not approved, check if we can continue iterating
            if iteration >= self.max_iterations:
                logger.warning(f"Maximum iterations ({self.max_iterations}) reached without approval")
                return {
                    "success": False,
                    "error": "Maximum iterations reached without approval",
                    "final_iteration": iteration,
                    "final_quality_score": tech_lead_result["quality_score"],
                    "workflow_context": workflow_context
                }
            
            # PM Agent Refinement
            refinement_result = self._execute_pm_refinement(current_ticket_draft, tech_lead_result, workflow_context, iteration)
            
            if not refinement_result["success"]:
                return refinement_result
            
            # Update for next iteration
            current_ticket_draft = refinement_result["refined_draft"]
            iteration += 1
        
        # Should not reach here, but safety net
        return {
            "success": False,
            "error": "Quality improvement loop completed without resolution",
            "workflow_context": workflow_context
        }
    
    def _execute_tech_lead_review(self, ticket_draft: Dict[str, Any], pm_analysis: Dict[str, Any], 
                                workflow_context: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """Execute Tech Lead Agent review"""
        
        logger.info(f"Tech Lead review - iteration {iteration}")
        
        start_time = time.time()
        tech_lead_result = self.tech_lead_agent.review_ticket_draft(ticket_draft, pm_analysis)
        execution_time = time.time() - start_time
        
        # Track interaction
        workflow_context["agent_interactions"].append({
            "agent": "Tech Lead Agent",
            "phase": f"review_iteration_{iteration}",
            "execution_time": execution_time,
            "result": "success" if tech_lead_result["success"] else "failure",
            "approval_status": tech_lead_result.get("approval_status", "unknown"),
            "quality_score": tech_lead_result.get("quality_score", 0)
        })
        
        if tech_lead_result["success"]:
            # Track quality history
            workflow_context["quality_history"].append({
                "iteration": iteration,
                "agent": "Tech Lead Agent",
                "quality_score": tech_lead_result["quality_score"],
                "approval_status": tech_lead_result["approval_status"],
                "passes_threshold": tech_lead_result["quality_score"] >= self.quality_threshold
            })
        
        return tech_lead_result
    
    def _execute_pm_refinement(self, ticket_draft: Dict[str, Any], tech_lead_feedback: Dict[str, Any],
                             workflow_context: Dict[str, Any], iteration: int) -> Dict[str, Any]:
        """Execute PM Agent refinement based on Tech Lead feedback"""
        
        logger.info(f"PM Agent refinement - iteration {iteration}")
        
        start_time = time.time()
        refinement_result = self.pm_agent.refine_ticket_draft(ticket_draft, tech_lead_feedback)
        execution_time = time.time() - start_time
        
        # Track interaction
        workflow_context["agent_interactions"].append({
            "agent": "PM Agent",
            "phase": f"refinement_iteration_{iteration}",
            "execution_time": execution_time,
            "result": "success" if refinement_result["success"] else "failure",
            "quality_score": refinement_result.get("quality_assessment", {}).get("overall_score", 0)
        })
        
        if refinement_result["success"]:
            # Track quality history
            workflow_context["quality_history"].append({
                "iteration": iteration,
                "agent": "PM Agent (Refinement)",
                "quality_score": refinement_result["quality_assessment"]["overall_score"],
                "passes_threshold": refinement_result["quality_assessment"]["passes_quality_gate"]
            })
        
        return refinement_result
    
    def _execute_ticket_creation(self, final_result: Dict[str, Any], workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute final ticket creation"""
        
        logger.info("Phase 3: Final Ticket Creation")
        
        # Prepare workflow metadata for ticket creation
        creation_context = {
            "final_quality_score": final_result["final_quality_score"],
            "tech_lead_approval": final_result["tech_lead_approval"],
            "iteration_count": final_result["iterations_completed"],
            "creation_timestamp": datetime.now().isoformat(),
            "workflow_id": workflow_context["workflow_id"]
        }
        
        start_time = time.time()
        creation_result = self.jira_creator_agent.create_final_ticket(
            final_result["final_ticket_draft"],
            creation_context
        )
        execution_time = time.time() - start_time
        
        # Track interaction
        workflow_context["agent_interactions"].append({
            "agent": "Jira Creator Agent",
            "phase": "final_creation",
            "execution_time": execution_time,
            "result": "success" if creation_result["success"] else "failure",
            "ticket_created": creation_result.get("ticket_created", False),
            "ticket_key": creation_result.get("ticket_key", "N/A")
        })
        
        return creation_result
    
    def _create_success_response(self, creation_result: Dict[str, Any], workflow_context: Dict[str, Any], 
                               workflow_duration: float) -> Dict[str, Any]:
        """Create comprehensive success response"""
        
        # Calculate workflow statistics
        stats = self._calculate_workflow_statistics(workflow_context, workflow_duration)
        
        return {
            "success": True,
            "workflow_completed": True,
            "workflow_id": workflow_context["workflow_id"],
            "ticket_created": creation_result.get("ticket_created", False),
            "ticket_key": creation_result.get("ticket_key"),
            "ticket_url": creation_result.get("ticket_url"),
            "workflow_statistics": stats,
            "quality_metrics": {
                "final_quality_score": creation_result.get("workflow_summary", {}).get("quality_score", "N/A"),
                "iterations_required": workflow_context["iteration_count"],
                "quality_threshold_met": True,
                "quality_history": workflow_context["quality_history"]
            },
            "agent_performance": {
                "pm_agent": "✅ Completed analysis and refinements",
                "tech_lead_agent": "✅ Approved final ticket",
                "jira_creator_agent": "✅ Successfully created ticket"
            },
            "next_steps": creation_result.get("next_steps", []),
            "workflow_metadata": workflow_context
        }
    
    def _create_failure_response(self, workflow_context: Dict[str, Any], failure_reason: str, 
                               error_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive failure response"""
        
        return {
            "success": False,
            "workflow_completed": False,
            "workflow_id": workflow_context.get("workflow_id", "unknown"),
            "failure_reason": failure_reason,
            "error_details": error_details,
            "workflow_progress": {
                "iterations_completed": workflow_context.get("iteration_count", 0),
                "agent_interactions": workflow_context.get("agent_interactions", []),
                "quality_history": workflow_context.get("quality_history", [])
            },
            "troubleshooting_recommendations": [
                "Review error details for specific issues",
                "Check Cloud Function connectivity",
                "Validate API credentials and permissions",
                "Consider simplifying user request if complexity is too high",
                "Retry with additional context if needed"
            ],
            "retry_possible": True
        }
    
    def _calculate_workflow_statistics(self, workflow_context: Dict[str, Any], total_duration: float) -> Dict[str, Any]:
        """Calculate comprehensive workflow statistics"""
        
        interactions = workflow_context.get("agent_interactions", [])
        quality_history = workflow_context.get("quality_history", [])
        
        # Execution time analysis
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
                "jira_creator_agent": round(jira_creator_time, 2)
            },
            "iteration_count": workflow_context.get("iteration_count", 0),
            "quality_improvement": round(quality_improvement, 2),
            "quality_score_range": {
                "minimum": min(quality_scores) if quality_scores else 0,
                "maximum": max(quality_scores) if quality_scores else 0,
                "final": quality_scores[-1] if quality_scores else 0
            },
            "agent_interaction_count": len(interactions),
            "efficiency_metrics": {
                "avg_iteration_time": round(total_duration / max(workflow_context.get("iteration_count", 1), 1), 2),
                "quality_threshold_achieved": max(quality_scores) >= self.quality_threshold if quality_scores else False,
                "iterations_to_approval": workflow_context.get("iteration_count", 0)
            }
        }


# Convenience function for easy usage
def create_jira_ticket_with_ai(user_request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to create a Jira ticket using the multi-agent system
    
    Args:
        user_request: User's request or requirement
        context: Additional context information
        
    Returns:
        Dictionary containing complete workflow results
    """
    orchestrator = MultiAgentOrchestrator()
    return orchestrator.create_jira_ticket(user_request, context)


# Export main classes and functions
__all__ = ["MultiAgentOrchestrator", "create_jira_ticket_with_ai"]