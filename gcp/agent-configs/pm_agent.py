#!/usr/bin/env python3

"""
PM Agent - Primary Product Manager Agent
Analyzes user requests and creates initial ticket drafts with GitBook context
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

class PMAgent:
    """Primary Product Manager Agent for analyzing requests and creating ticket drafts"""
    
    def __init__(self, project_id: str = "service-execution-uat-bb7", location: str = "europe-west9"):
        self.project_id = project_id
        self.location = location
        self.tools = CloudFunctionTools(project_id)
        self.quality_gates = QualityGates()
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Agent configuration
        self.model_name = "gemini-2.5-flash"
        self.agent_instructions = self._get_agent_instructions()
        
        logger.info(f"PM Agent initialized for project {project_id} in {location}")
    
    def analyze_user_request(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user request and create initial ticket draft with GitBook context
        
        Args:
            user_request: The user's request/requirement
            context: Additional context information
            
        Returns:
            Dictionary containing analysis results and ticket draft
        """
        try:
            logger.info(f"Analyzing user request: {user_request[:100]}...")
            
            # Step 1: Research relevant GitBook content
            gitbook_context = self._research_gitbook_context(user_request)
            
            # Step 2: Analyze existing Jira tickets for patterns
            jira_context = self._analyze_jira_patterns()
            
            # Step 3: Generate initial ticket draft
            ticket_draft = self._generate_ticket_draft(
                user_request, 
                gitbook_context, 
                jira_context,
                context
            )
            
            # Step 4: Perform initial quality assessment
            quality_assessment = self.quality_gates.calculate_quality_score(ticket_draft)
            
            return {
                "success": True,
                "user_request": user_request,
                "ticket_draft": ticket_draft,
                "quality_assessment": quality_assessment,
                "gitbook_context": gitbook_context,
                "jira_context": jira_context,
                "agent": "PM Agent",
                "next_step": "tech_lead_review" if quality_assessment["passes_quality_gate"] else "refinement_needed"
            }
            
        except Exception as e:
            logger.error(f"PM Agent analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "PM Agent"
            }
    
    def refine_ticket_draft(self, original_draft: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine ticket draft based on Tech Lead feedback
        
        Args:
            original_draft: Original ticket draft
            feedback: Feedback from Tech Lead Agent
            
        Returns:
            Refined ticket draft
        """
        try:
            logger.info("Refining ticket draft based on feedback")
            
            # Generate refined version using feedback
            refined_draft = self._refine_with_feedback(original_draft, feedback)
            
            # Re-assess quality
            quality_assessment = self.quality_gates.calculate_quality_score(refined_draft)
            
            return {
                "success": True,
                "refined_draft": refined_draft,
                "quality_assessment": quality_assessment,
                "iteration": original_draft.get("iteration", 0) + 1,
                "agent": "PM Agent",
                "refinement_applied": True
            }
            
        except Exception as e:
            logger.error(f"PM Agent refinement error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "PM Agent"
            }
    
    def _research_gitbook_context(self, user_request: str) -> Dict[str, Any]:
        """Research relevant GitBook documentation"""
        # Extract key terms from user request for search
        search_terms = self._extract_search_terms(user_request)
        
        gitbook_results = []
        for term in search_terms:
            result = self.tools.search_gitbook_content(term)
            if result["success"]:
                gitbook_results.append(result)
        
        return {
            "search_terms": search_terms,
            "results": gitbook_results,
            "relevant_content": self._consolidate_gitbook_content(gitbook_results)
        }
    
    def _analyze_jira_patterns(self) -> Dict[str, Any]:
        """Analyze existing Jira tickets for patterns and context"""
        return self.tools.analyze_existing_jira_tickets()
    
    def _generate_ticket_draft(self, user_request: str, gitbook_context: Dict, jira_context: Dict, additional_context: Dict = None) -> Dict[str, Any]:
        """Generate initial ticket draft using AI model"""
        
        # Prepare context for AI model
        context_summary = self._prepare_context_summary(gitbook_context, jira_context)
        
        # Create prompt for ticket generation
        prompt = self._create_ticket_generation_prompt(user_request, context_summary, additional_context)
        
        # Use Vertex AI to generate ticket
        ticket_draft = self._call_vertex_ai_for_ticket_generation(prompt)
        
        return ticket_draft
    
    def _refine_with_feedback(self, original_draft: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Refine ticket draft based on feedback"""
        
        # Create refinement prompt
        refinement_prompt = self._create_refinement_prompt(original_draft, feedback)
        
        # Use Vertex AI to refine ticket
        refined_draft = self._call_vertex_ai_for_refinement(refinement_prompt)
        
        return refined_draft
    
    def _extract_search_terms(self, user_request: str) -> List[str]:
        """Extract key search terms from user request"""
        # Simple keyword extraction - can be enhanced with NLP
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can'}
        
        words = user_request.lower().split()
        keywords = [word.strip('.,!?') for word in words if word.lower() not in common_words and len(word) > 3]
        
        # Return top 3 keywords
        return keywords[:3] if keywords else [user_request[:50]]
    
    def _consolidate_gitbook_content(self, gitbook_results: List[Dict]) -> str:
        """Consolidate GitBook search results into relevant content"""
        content_pieces = []
        for result in gitbook_results:
            if result["success"] and result["content"]:
                content_pieces.append(result["content"][:500])  # First 500 chars
        
        return "\n\n".join(content_pieces)
    
    def _prepare_context_summary(self, gitbook_context: Dict, jira_context: Dict) -> str:
        """Prepare context summary for AI model"""
        context_parts = []
        
        # GitBook context
        if gitbook_context.get("relevant_content"):
            context_parts.append(f"GitBook Documentation Context:\n{gitbook_context['relevant_content']}")
        
        # Jira patterns context
        if jira_context.get("success") and jira_context.get("patterns"):
            patterns = jira_context["patterns"]
            context_parts.append(f"Jira Project Patterns:\n- Common issue type: {patterns.get('most_common_issue_type')}\n- Common priority: {patterns.get('most_common_priority')}\n- Available components: {', '.join(patterns.get('available_components', []))}")
        
        return "\n\n".join(context_parts)
    
    def _create_ticket_generation_prompt(self, user_request: str, context_summary: str, additional_context: Dict = None) -> str:
        """Create prompt for ticket generation"""
        
        prompt = f"""
You are a Senior Product Manager creating a comprehensive Jira ticket. You must follow these standards:

USER REQUEST:
{user_request}

RELEVANT CONTEXT:
{context_summary}

ADDITIONAL CONTEXT:
{json.dumps(additional_context) if additional_context else 'None'}

REQUIREMENTS:
1. Create a clear, actionable summary (10-80 characters)
2. Write a proper user story in format: "As a [user type] I want [goal] so that [benefit]"
3. Include at least 3 detailed acceptance criteria
4. Consider technical feasibility and existing system patterns
5. Ensure business value is clear

JIRA TICKET FORMAT:
Please provide a JSON response with:
{{
    "summary": "Clear action-oriented title",
    "description": "Full user story with acceptance criteria",
    "issue_type": "Story|Task|Bug|Epic",
    "priority": "Low|Medium|High|Critical",
    "labels": ["relevant", "labels"],
    "components": ["if-applicable"],
    "business_value": "Clear explanation of value",
    "technical_notes": "Implementation considerations"
}}

Focus on creating a ticket that meets Definition of Ready standards.
"""
        return prompt
    
    def _create_refinement_prompt(self, original_draft: Dict[str, Any], feedback: Dict[str, Any]) -> str:
        """Create prompt for ticket refinement"""
        
        prompt = f"""
You are refining a Jira ticket based on Tech Lead feedback. Improve the ticket while preserving good elements.

ORIGINAL TICKET DRAFT:
{json.dumps(original_draft, indent=2)}

TECH LEAD FEEDBACK:
{json.dumps(feedback, indent=2)}

REFINEMENT INSTRUCTIONS:
1. Address all feedback points while maintaining ticket quality
2. Improve technical feasibility based on feedback
3. Enhance acceptance criteria if needed
4. Maintain proper user story format
5. Ensure the refined ticket will score ≥ 0.8 on quality assessment

Please provide the refined ticket in the same JSON format as the original.
"""
        return prompt
    
    def _call_vertex_ai_for_ticket_generation(self, prompt: str) -> Dict[str, Any]:
        """Call Vertex AI model for ticket generation"""
        try:
            # This is a simplified implementation
            # In a real implementation, you would use the Vertex AI SDK properly
            # For now, return a structured ticket format
            
            return {
                "summary": "Implement user request feature",
                "description": "As a user I want to implement the requested feature so that I can achieve my goals.\n\nAcceptance Criteria:\n- Feature is implemented according to requirements\n- Feature is tested and validated\n- Feature meets quality standards",
                "issue_type": "Story",
                "priority": "Medium",
                "labels": ["ai-generated", "pm-agent"],
                "components": [],
                "business_value": "Improves user experience and system functionality",
                "technical_notes": "Implementation should follow existing patterns and architecture"
            }
            
        except Exception as e:
            logger.error(f"Vertex AI call error: {str(e)}")
            raise e
    
    def _call_vertex_ai_for_refinement(self, prompt: str) -> Dict[str, Any]:
        """Call Vertex AI model for ticket refinement"""
        try:
            # Simplified implementation - would use actual Vertex AI SDK
            return {
                "summary": "Refined user request implementation",
                "description": "As a user I want to implement the refined feature so that I can achieve improved goals.\n\nAcceptance Criteria:\n- Refined feature is implemented according to updated requirements\n- Feature addresses all feedback points\n- Feature exceeds quality thresholds\n- Feature is thoroughly tested",
                "issue_type": "Story", 
                "priority": "Medium",
                "labels": ["ai-generated", "pm-agent", "refined"],
                "components": [],
                "business_value": "Enhanced user experience with improved functionality",
                "technical_notes": "Refined implementation addresses technical feedback and constraints"
            }
            
        except Exception as e:
            logger.error(f"Vertex AI refinement call error: {str(e)}")
            raise e
    
    def _get_agent_instructions(self) -> str:
        """Get agent instructions and personality"""
        return """
You are a Senior Product Manager AI Agent specialized in creating high-quality Jira tickets.

Your responsibilities:
1. Analyze user requests for business value and feasibility
2. Research relevant documentation and context
3. Create comprehensive user stories with detailed acceptance criteria
4. Ensure tickets meet Definition of Ready standards
5. Collaborate with Tech Lead Agent for quality validation
6. Iteratively refine tickets based on feedback

Your personality:
- Detail-oriented and thorough
- Business-value focused
- Collaborative and receptive to feedback
- Quality-driven with high standards
- User-centric in approach

Quality Standards:
- All tickets must score ≥ 0.8 on quality assessment
- User stories must follow proper format
- Acceptance criteria must be testable and complete
- Technical feasibility must be realistic
- Business value must be clearly articulated
"""


# Export the PM Agent class
__all__ = ["PMAgent"]