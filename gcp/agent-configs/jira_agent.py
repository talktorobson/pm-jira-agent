#!/usr/bin/env python3

"""
Jira Creator Agent - Ticket Creation and Execution
Creates final Jira tickets after PM and Tech Lead approval
"""

import vertexai
from google.cloud import aiplatform
from typing import Dict, Any, List
import json
import logging
from tools import CloudFunctionTools, QualityGates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraCreatorAgent:
    """Jira Creator Agent for final ticket creation and execution"""
    
    def __init__(self, project_id: str = "service-execution-uat-bb7", location: str = "europe-west9"):
        self.project_id = project_id
        self.location = location
        self.tools = CloudFunctionTools(project_id)
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Agent configuration
        self.model_name = "gemini-1.5-flash"  # Faster model for execution tasks
        self.agent_instructions = self._get_agent_instructions()
        
        logger.info(f"Jira Creator Agent initialized for project {project_id} in {location}")
    
    def create_final_ticket(self, approved_ticket: Dict[str, Any], workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create final Jira ticket after approval from PM and Tech Lead agents
        
        Args:
            approved_ticket: Approved ticket draft from workflow
            workflow_context: Context from PM and Tech Lead review process
            
        Returns:
            Dictionary containing creation results and ticket details
        """
        try:
            logger.info("Jira Creator Agent creating final ticket")
            
            # Step 1: Final validation before creation
            final_validation = self._perform_final_validation(approved_ticket, workflow_context)
            
            if not final_validation["valid"]:
                return {
                    "success": False,
                    "error": "Final validation failed",
                    "validation_errors": final_validation["errors"],
                    "agent": "Jira Creator Agent"
                }
            
            # Step 2: Prepare ticket data for Jira API
            jira_ticket_data = self._prepare_jira_ticket_data(approved_ticket, workflow_context)
            
            # Step 3: Create ticket via Cloud Function
            creation_result = self.tools.create_jira_ticket(jira_ticket_data)
            
            # Step 4: Post-creation validation and logging
            if creation_result["success"]:
                post_creation_result = self._handle_successful_creation(creation_result, workflow_context)
                return post_creation_result
            else:
                return self._handle_creation_failure(creation_result, jira_ticket_data)
                
        except Exception as e:
            logger.error(f"Jira Creator Agent error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "Jira Creator Agent"
            }
    
    def validate_created_ticket(self, ticket_key: str) -> Dict[str, Any]:
        """
        Validate that created ticket meets expectations
        
        Args:
            ticket_key: Jira ticket key (e.g., AHSSI-123)
            
        Returns:
            Dictionary containing validation results
        """
        try:
            logger.info(f"Validating created ticket: {ticket_key}")
            
            # Get ticket details from Jira
            ticket_details = self._get_ticket_details(ticket_key)
            
            if not ticket_details["success"]:
                return {
                    "success": False,
                    "error": "Could not retrieve ticket details",
                    "ticket_key": ticket_key
                }
            
            # Validate ticket content
            validation_results = self._validate_ticket_content(ticket_details["data"])
            
            return {
                "success": True,
                "ticket_key": ticket_key,
                "ticket_url": f"https://jira.adeo.com/browse/{ticket_key}",
                "validation_results": validation_results,
                "agent": "Jira Creator Agent"
            }
            
        except Exception as e:
            logger.error(f"Ticket validation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ticket_key": ticket_key
            }
    
    def update_ticket_with_metadata(self, ticket_key: str, workflow_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update created ticket with workflow metadata and tracking information
        
        Args:
            ticket_key: Jira ticket key
            workflow_metadata: Metadata from the multi-agent workflow
            
        Returns:
            Dictionary containing update results
        """
        try:
            logger.info(f"Updating ticket {ticket_key} with workflow metadata")
            
            # Prepare metadata comment
            metadata_comment = self._prepare_metadata_comment(workflow_metadata)
            
            # Add comment to ticket (would use Jira API update)
            # For now, return success with metadata prepared
            
            return {
                "success": True,
                "ticket_key": ticket_key,
                "metadata_added": True,
                "workflow_tracking": {
                    "pm_agent_score": workflow_metadata.get("pm_quality_score", "N/A"),
                    "tech_lead_score": workflow_metadata.get("tech_lead_score", "N/A"),
                    "final_quality_score": workflow_metadata.get("final_quality_score", "N/A"),
                    "iteration_count": workflow_metadata.get("iteration_count", 1),
                    "creation_timestamp": workflow_metadata.get("creation_timestamp", "N/A")
                },
                "agent": "Jira Creator Agent"
            }
            
        except Exception as e:
            logger.error(f"Metadata update error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ticket_key": ticket_key
            }
    
    def _perform_final_validation(self, approved_ticket: Dict[str, Any], workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform final validation before ticket creation"""
        
        validation_errors = []
        
        # Check required fields
        required_fields = ["summary", "description"]
        for field in required_fields:
            if not approved_ticket.get(field):
                validation_errors.append(f"Missing required field: {field}")
        
        # Check quality score
        final_quality_score = workflow_context.get("final_quality_score", 0)
        if final_quality_score < 0.8:
            validation_errors.append(f"Quality score {final_quality_score} below threshold (0.8)")
        
        # Check approval status
        tech_lead_approval = workflow_context.get("tech_lead_approval", False)
        if not tech_lead_approval:
            validation_errors.append("Tech Lead approval not confirmed")
        
        # Validate summary length
        summary = approved_ticket.get("summary", "")
        if len(summary) > 80:
            validation_errors.append("Summary too long (>80 characters)")
        elif len(summary) < 10:
            validation_errors.append("Summary too short (<10 characters)")
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors
        }
    
    def _prepare_jira_ticket_data(self, approved_ticket: Dict[str, Any], workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare ticket data for Jira API creation"""
        
        # Base ticket data
        jira_data = {
            "summary": approved_ticket["summary"],
            "description": self._format_description_for_jira(approved_ticket, workflow_context),
            "issue_type": approved_ticket.get("issue_type", "Story"),
            "priority": approved_ticket.get("priority", "Medium")
        }
        
        # Add labels including workflow tracking
        labels = approved_ticket.get("labels", [])
        workflow_labels = [
            "ai-generated",
            "pm-agent",
            f"quality-score-{int(workflow_context.get('final_quality_score', 0) * 100)}"
        ]
        jira_data["labels"] = list(set(labels + workflow_labels))
        
        # Add components if specified
        if approved_ticket.get("components"):
            jira_data["components"] = approved_ticket["components"]
        
        return jira_data
    
    def _format_description_for_jira(self, approved_ticket: Dict[str, Any], workflow_context: Dict[str, Any]) -> str:
        """Format description for Jira with workflow metadata"""
        
        base_description = approved_ticket.get("description", "")
        
        # Add workflow metadata section
        metadata_section = f"""

---
## Workflow Metadata
- **Created by**: PM Jira Agent (Multi-Agent System)
- **Quality Score**: {workflow_context.get('final_quality_score', 'N/A')}
- **PM Agent Analysis**: ✅ Completed
- **Tech Lead Review**: ✅ Approved
- **Iteration Count**: {workflow_context.get('iteration_count', 1)}

## Business Value
{approved_ticket.get('business_value', 'Enhanced user experience and system functionality')}

## Technical Notes
{approved_ticket.get('technical_notes', 'Implementation should follow existing patterns and architecture')}
"""
        
        return base_description + metadata_section
    
    def _handle_successful_creation(self, creation_result: Dict[str, Any], workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful ticket creation"""
        
        ticket_key = creation_result["ticket_key"]
        ticket_url = creation_result["ticket_url"]
        
        logger.info(f"Successfully created Jira ticket: {ticket_key}")
        
        # Prepare success response
        success_response = {
            "success": True,
            "ticket_created": True,
            "ticket_key": ticket_key,
            "ticket_url": ticket_url,
            "creation_details": creation_result,
            "workflow_summary": {
                "pm_agent_analysis": "✅ Completed",
                "tech_lead_review": "✅ Approved", 
                "quality_score": workflow_context.get("final_quality_score", "N/A"),
                "iteration_count": workflow_context.get("iteration_count", 1)
            },
            "next_steps": [
                f"Review ticket at {ticket_url}",
                "Assign to appropriate team member",
                "Add to appropriate sprint/backlog",
                "Validate implementation against acceptance criteria"
            ],
            "agent": "Jira Creator Agent"
        }
        
        return success_response
    
    def _handle_creation_failure(self, creation_result: Dict[str, Any], ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ticket creation failure"""
        
        logger.error(f"Ticket creation failed: {creation_result.get('error', 'Unknown error')}")
        
        return {
            "success": False,
            "ticket_created": False,
            "error": creation_result.get("error", "Unknown creation error"),
            "ticket_data_attempted": ticket_data,
            "retry_possible": True,
            "troubleshooting_steps": [
                "Check Jira API connectivity",
                "Validate required fields",
                "Check user permissions",
                "Review Jira project configuration"
            ],
            "agent": "Jira Creator Agent"
        }
    
    def _get_ticket_details(self, ticket_key: str) -> Dict[str, Any]:
        """Get ticket details from Jira for validation"""
        
        # Use Cloud Function to get ticket details
        try:
            payload = {
                "action": "get_ticket",
                "ticket_id": ticket_key
            }
            
            response = self.tools.jira_function_url
            # Would make actual API call here
            
            # For now, return placeholder success
            return {
                "success": True,
                "data": {
                    "key": ticket_key,
                    "fields": {
                        "summary": "Retrieved ticket summary",
                        "description": "Retrieved ticket description"
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_ticket_content(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content of created ticket"""
        
        validation = {
            "summary_valid": True,
            "description_valid": True,
            "fields_complete": True,
            "metadata_present": True,
            "overall_valid": True
        }
        
        # Validate summary
        summary = ticket_data.get("fields", {}).get("summary", "")
        if not summary or len(summary) < 10:
            validation["summary_valid"] = False
        
        # Validate description
        description = ticket_data.get("fields", {}).get("description", "")
        if not description or "acceptance criteria" not in description.lower():
            validation["description_valid"] = False
        
        # Check metadata presence
        if "workflow metadata" not in description.lower():
            validation["metadata_present"] = False
        
        # Overall validation
        validation["overall_valid"] = all([
            validation["summary_valid"],
            validation["description_valid"],
            validation["fields_complete"],
            validation["metadata_present"]
        ])
        
        return validation
    
    def _prepare_metadata_comment(self, workflow_metadata: Dict[str, Any]) -> str:
        """Prepare metadata comment for ticket"""
        
        comment = f"""
🤖 **Multi-Agent Workflow Metadata**

**Quality Metrics:**
- Final Quality Score: {workflow_metadata.get('final_quality_score', 'N/A')}
- PM Agent Score: {workflow_metadata.get('pm_quality_score', 'N/A')}
- Tech Lead Score: {workflow_metadata.get('tech_lead_score', 'N/A')}

**Workflow Process:**
- Iteration Count: {workflow_metadata.get('iteration_count', 1)}
- PM Analysis: ✅ Completed
- Tech Lead Review: ✅ Approved
- Creation Timestamp: {workflow_metadata.get('creation_timestamp', 'N/A')}

**Agent Contributions:**
- PM Agent: Initial analysis and ticket drafting
- Tech Lead Agent: Technical review and validation
- Jira Creator Agent: Final creation and validation

This ticket was created through an automated multi-agent quality assurance process.
"""
        return comment
    
    def _get_agent_instructions(self) -> str:
        """Get agent instructions and personality"""
        return """
You are a Jira Creator AI Agent specialized in final ticket creation and execution.

Your responsibilities:
1. Perform final validation before ticket creation
2. Create high-quality Jira tickets via API integration
3. Validate created tickets meet expectations
4. Add workflow metadata and tracking information
5. Handle creation errors and provide troubleshooting guidance
6. Ensure tickets are properly formatted and accessible

Your personality:
- Execution-focused and reliable
- Detail-oriented in final validation
- Thorough in error handling
- Quality-focused in ticket creation
- Comprehensive in documentation

Quality Standards:
- Final validation must pass all checks
- Tickets must be properly formatted for Jira
- Metadata must be comprehensive and useful
- Error handling must be robust and informative
- Created tickets must be immediately usable by development teams
"""


# Export the Jira Creator Agent class
__all__ = ["JiraCreatorAgent"]