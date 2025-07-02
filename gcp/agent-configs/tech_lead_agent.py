#!/usr/bin/env python3

"""
Tech Lead Agent - Quality Review and Technical Validation
Reviews PM Agent ticket drafts and provides technical feedback
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

class TechLeadAgent:
    """Tech Lead Agent for technical review and quality validation"""
    
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
        
        logger.info(f"Tech Lead Agent initialized for project {project_id} in {location}")
    
    def review_ticket_draft(self, ticket_draft: Dict[str, Any], pm_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review ticket draft from PM Agent and provide technical feedback
        
        Args:
            ticket_draft: Ticket draft from PM Agent
            pm_analysis: PM Agent's analysis and context
            
        Returns:
            Dictionary containing review results and feedback
        """
        try:
            logger.info("Tech Lead reviewing ticket draft")
            
            # Step 1: Perform detailed quality assessment
            quality_assessment = self.quality_gates.calculate_quality_score(ticket_draft)
            
            # Step 2: Technical feasibility analysis
            technical_analysis = self._analyze_technical_feasibility(ticket_draft, pm_analysis)
            
            # Step 3: Acceptance criteria validation
            ac_validation = self._validate_acceptance_criteria(ticket_draft)
            
            # Step 4: Integration and dependency analysis
            dependency_analysis = self._analyze_dependencies(ticket_draft, pm_analysis)
            
            # Step 5: Generate comprehensive feedback
            feedback = self._generate_technical_feedback(
                ticket_draft,
                quality_assessment,
                technical_analysis,
                ac_validation,
                dependency_analysis
            )
            
            # Step 6: Make approval decision
            approval_decision = self._make_approval_decision(quality_assessment, feedback)
            
            return {
                "success": True,
                "approval_status": approval_decision["status"],
                "quality_score": quality_assessment["overall_score"],
                "quality_assessment": quality_assessment,
                "technical_analysis": technical_analysis,
                "acceptance_criteria_validation": ac_validation,
                "dependency_analysis": dependency_analysis,
                "feedback": feedback,
                "recommendations": approval_decision["recommendations"],
                "agent": "Tech Lead Agent",
                "next_step": approval_decision["next_step"]
            }
            
        except Exception as e:
            logger.error(f"Tech Lead Agent review error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "Tech Lead Agent"
            }
    
    def validate_refined_ticket(self, refined_draft: Dict[str, Any], original_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate refined ticket after PM Agent improvements
        
        Args:
            refined_draft: Refined ticket draft
            original_feedback: Original feedback provided
            
        Returns:
            Final validation results
        """
        try:
            logger.info("Tech Lead validating refined ticket")
            
            # Re-assess quality
            quality_assessment = self.quality_gates.calculate_quality_score(refined_draft)
            
            # Check if feedback was addressed
            feedback_addressed = self._validate_feedback_addressed(refined_draft, original_feedback)
            
            # Final approval decision
            final_decision = self._make_final_approval_decision(quality_assessment, feedback_addressed)
            
            return {
                "success": True,
                "final_approval": final_decision["approved"],
                "quality_score": quality_assessment["overall_score"],
                "feedback_addressed": feedback_addressed,
                "final_recommendations": final_decision["recommendations"],
                "agent": "Tech Lead Agent",
                "ready_for_creation": final_decision["approved"] and quality_assessment["overall_score"] >= 0.8
            }
            
        except Exception as e:
            logger.error(f"Tech Lead Agent validation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": "Tech Lead Agent"
            }
    
    def _analyze_technical_feasibility(self, ticket_draft: Dict[str, Any], pm_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical feasibility of the ticket"""
        
        analysis = {
            "feasibility_score": 0.7,  # Default reasonable score
            "complexity_assessment": "medium",
            "estimated_effort": "TBD",
            "technical_risks": [],
            "architecture_considerations": [],
            "implementation_approach": ""
        }
        
        summary = ticket_draft.get("summary", "").lower()
        description = ticket_draft.get("description", "").lower()
        
        # Analyze complexity indicators
        complexity_indicators = {
            "high": ["integration", "migration", "refactor", "architecture", "performance", "security"],
            "medium": ["feature", "enhancement", "update", "modify", "extend"],
            "low": ["fix", "bug", "typo", "text", "styling", "minor"]
        }
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in summary + description for indicator in indicators):
                analysis["complexity_assessment"] = complexity
                break
        
        # Assess technical risks
        risk_keywords = ["database", "api", "external", "third-party", "payment", "authentication"]
        for keyword in risk_keywords:
            if keyword in summary + description:
                analysis["technical_risks"].append(f"Involves {keyword} - requires careful testing")
        
        # Consider GitBook context for architecture alignment
        if pm_analysis.get("gitbook_context", {}).get("relevant_content"):
            analysis["architecture_considerations"].append("Reviewed against existing documentation")
        
        # Adjust feasibility score based on complexity
        complexity_scores = {"low": 0.9, "medium": 0.7, "high": 0.5}
        analysis["feasibility_score"] = complexity_scores.get(analysis["complexity_assessment"], 0.7)
        
        # Effort estimation
        effort_mapping = {"low": "1-2 days", "medium": "3-5 days", "high": "1-2 weeks"}
        analysis["estimated_effort"] = effort_mapping.get(analysis["complexity_assessment"], "TBD")
        
        analysis["implementation_approach"] = self._suggest_implementation_approach(ticket_draft)
        
        return analysis
    
    def _validate_acceptance_criteria(self, ticket_draft: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality and completeness of acceptance criteria"""
        
        description = ticket_draft.get("description", "")
        validation = {
            "criteria_count": 0,
            "criteria_quality": "poor",
            "testable_criteria": 0,
            "specific_criteria": 0,
            "missing_elements": [],
            "recommendations": []
        }
        
        # Count criteria (look for bullets, numbers, "given/when/then")
        criteria_patterns = [
            description.count("•"),
            description.count("-"),
            description.count("*"),
            len([line for line in description.split("\n") if line.strip() and line.strip()[0].isdigit()]),
            description.lower().count("given"),
            description.lower().count("when"),
            description.lower().count("then")
        ]
        
        validation["criteria_count"] = max(criteria_patterns)
        
        # Assess testability
        testable_keywords = ["should", "must", "will", "verify", "confirm", "validate", "check"]
        validation["testable_criteria"] = sum(1 for keyword in testable_keywords if keyword in description.lower())
        
        # Assess specificity
        specific_keywords = ["exactly", "within", "at least", "no more than", "specific", "particular"]
        validation["specific_criteria"] = sum(1 for keyword in specific_keywords if keyword in description.lower())
        
        # Quality assessment
        if validation["criteria_count"] >= 3 and validation["testable_criteria"] >= 2:
            validation["criteria_quality"] = "good"
        elif validation["criteria_count"] >= 2:
            validation["criteria_quality"] = "fair"
        else:
            validation["criteria_quality"] = "poor"
        
        # Identify missing elements
        if validation["criteria_count"] < 3:
            validation["missing_elements"].append("Insufficient acceptance criteria (minimum 3 required)")
        
        if validation["testable_criteria"] < 2:
            validation["missing_elements"].append("Criteria lack testable conditions")
        
        if "user interface" in description.lower() and "ui" not in description.lower():
            validation["missing_elements"].append("UI/UX criteria may be needed")
        
        # Generate recommendations
        if validation["criteria_quality"] != "good":
            validation["recommendations"].extend([
                "Add more specific, testable acceptance criteria",
                "Use Given/When/Then format for complex scenarios",
                "Include edge cases and error handling",
                "Specify measurable success criteria"
            ])
        
        return validation
    
    def _analyze_dependencies(self, ticket_draft: Dict[str, Any], pm_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze dependencies and integration points"""
        
        dependencies = {
            "internal_dependencies": [],
            "external_dependencies": [],
            "api_integrations": [],
            "database_changes": False,
            "ui_changes": False,
            "breaking_changes": False,
            "risk_level": "low"
        }
        
        summary = ticket_draft.get("summary", "").lower()
        description = ticket_draft.get("description", "").lower()
        full_text = summary + " " + description
        
        # Check for internal dependencies
        internal_keywords = ["authentication", "user management", "permissions", "config"]
        for keyword in internal_keywords:
            if keyword in full_text:
                dependencies["internal_dependencies"].append(keyword)
        
        # Check for external dependencies
        external_keywords = ["api", "third-party", "external", "service", "integration"]
        for keyword in external_keywords:
            if keyword in full_text:
                dependencies["external_dependencies"].append(keyword)
        
        # Check for specific integrations (based on our Cloud Functions)
        if "gitbook" in full_text or "documentation" in full_text:
            dependencies["api_integrations"].append("GitBook API")
        
        if "jira" in full_text or "ticket" in full_text:
            dependencies["api_integrations"].append("Jira API")
        
        # Check for database changes
        db_keywords = ["database", "schema", "table", "migration", "data"]
        dependencies["database_changes"] = any(keyword in full_text for keyword in db_keywords)
        
        # Check for UI changes
        ui_keywords = ["interface", "ui", "frontend", "display", "view", "screen"]
        dependencies["ui_changes"] = any(keyword in full_text for keyword in ui_keywords)
        
        # Check for breaking changes
        breaking_keywords = ["remove", "delete", "deprecate", "replace", "breaking"]
        dependencies["breaking_changes"] = any(keyword in full_text for keyword in breaking_keywords)
        
        # Assess risk level
        risk_factors = (
            len(dependencies["external_dependencies"]) +
            len(dependencies["api_integrations"]) +
            (1 if dependencies["database_changes"] else 0) +
            (1 if dependencies["breaking_changes"] else 0)
        )
        
        if risk_factors >= 3:
            dependencies["risk_level"] = "high"
        elif risk_factors >= 2:
            dependencies["risk_level"] = "medium"
        else:
            dependencies["risk_level"] = "low"
        
        return dependencies
    
    def _generate_technical_feedback(self, ticket_draft: Dict[str, Any], quality_assessment: Dict[str, Any], 
                                   technical_analysis: Dict[str, Any], ac_validation: Dict[str, Any], 
                                   dependency_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive technical feedback"""
        
        feedback = {
            "overall_feedback": "",
            "technical_concerns": [],
            "quality_improvements": [],
            "implementation_suggestions": [],
            "risk_mitigation": [],
            "priority_adjustments": []
        }
        
        # Overall feedback based on quality score
        if quality_assessment["overall_score"] >= 0.8:
            feedback["overall_feedback"] = "Ticket meets quality standards with minor recommendations"
        elif quality_assessment["overall_score"] >= 0.6:
            feedback["overall_feedback"] = "Ticket needs improvement before approval"
        else:
            feedback["overall_feedback"] = "Ticket requires significant revision"
        
        # Technical concerns
        if technical_analysis["complexity_assessment"] == "high":
            feedback["technical_concerns"].append("High complexity - consider breaking into smaller tickets")
        
        if technical_analysis["technical_risks"]:
            feedback["technical_concerns"].extend(technical_analysis["technical_risks"])
        
        if dependency_analysis["risk_level"] == "high":
            feedback["technical_concerns"].append("High dependency risk - ensure integration testing")
        
        # Quality improvements
        if ac_validation["criteria_quality"] != "good":
            feedback["quality_improvements"].extend(ac_validation["recommendations"])
        
        for area, score in quality_assessment["detailed_scores"].items():
            if score < 0.7:
                feedback["quality_improvements"].append(f"Improve {area.replace('_', ' ')}")
        
        # Implementation suggestions
        if technical_analysis["implementation_approach"]:
            feedback["implementation_suggestions"].append(technical_analysis["implementation_approach"])
        
        if dependency_analysis["database_changes"]:
            feedback["implementation_suggestions"].append("Include database migration strategy")
        
        if dependency_analysis["ui_changes"]:
            feedback["implementation_suggestions"].append("Include UI/UX design considerations")
        
        # Risk mitigation
        if dependency_analysis["breaking_changes"]:
            feedback["risk_mitigation"].append("Implement backward compatibility or migration plan")
        
        if dependency_analysis["external_dependencies"]:
            feedback["risk_mitigation"].append("Add fallback mechanisms for external dependencies")
        
        # Priority adjustments
        if technical_analysis["complexity_assessment"] == "high" and ticket_draft.get("priority") == "High":
            feedback["priority_adjustments"].append("Consider reducing priority due to high complexity")
        
        return feedback
    
    def _make_approval_decision(self, quality_assessment: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Make approval decision based on assessment"""
        
        quality_score = quality_assessment["overall_score"]
        has_major_concerns = len(feedback["technical_concerns"]) > 2
        
        if quality_score >= 0.8 and not has_major_concerns:
            return {
                "status": "approved",
                "next_step": "create_ticket",
                "recommendations": ["Ticket approved for creation"]
            }
        elif quality_score >= 0.6:
            return {
                "status": "needs_improvement",
                "next_step": "refine_ticket",
                "recommendations": feedback["quality_improvements"] + feedback["technical_concerns"]
            }
        else:
            return {
                "status": "rejected",
                "next_step": "major_revision",
                "recommendations": ["Significant revision required"] + feedback["quality_improvements"]
            }
    
    def _make_final_approval_decision(self, quality_assessment: Dict[str, Any], feedback_addressed: Dict[str, Any]) -> Dict[str, Any]:
        """Make final approval decision for refined ticket"""
        
        quality_score = quality_assessment["overall_score"]
        feedback_score = feedback_addressed["percentage_addressed"]
        
        approved = quality_score >= 0.8 and feedback_score >= 0.7
        
        recommendations = []
        if not approved:
            if quality_score < 0.8:
                recommendations.append(f"Quality score {quality_score} below threshold (0.8)")
            if feedback_score < 0.7:
                recommendations.append(f"Feedback addressed {feedback_score}% - below threshold (70%)")
        else:
            recommendations.append("Ticket approved for final creation")
        
        return {
            "approved": approved,
            "recommendations": recommendations
        }
    
    def _validate_feedback_addressed(self, refined_draft: Dict[str, Any], original_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that original feedback was addressed in refined draft"""
        
        # Simplified validation - in real implementation would be more sophisticated
        return {
            "percentage_addressed": 0.8,  # Placeholder
            "addressed_points": ["Quality improvements applied", "Technical concerns addressed"],
            "remaining_issues": []
        }
    
    def _suggest_implementation_approach(self, ticket_draft: Dict[str, Any]) -> str:
        """Suggest implementation approach based on ticket content"""
        
        description = ticket_draft.get("description", "").lower()
        
        if "api" in description:
            return "Consider API-first approach with proper error handling and testing"
        elif "ui" in description or "interface" in description:
            return "Start with wireframes and user testing before implementation"
        elif "database" in description:
            return "Design schema changes carefully with migration strategy"
        else:
            return "Follow standard development workflow with testing at each stage"
    
    def _get_agent_instructions(self) -> str:
        """Get agent instructions and personality"""
        return """
You are a Senior Tech Lead AI Agent specialized in technical review and quality assurance.

Your responsibilities:
1. Review PM Agent ticket drafts for technical feasibility
2. Validate acceptance criteria completeness and quality
3. Analyze dependencies and integration points
4. Assess technical risks and complexity
5. Provide constructive feedback for improvement
6. Ensure tickets meet technical and quality standards

Your personality:
- Technically rigorous and detail-oriented
- Constructive and helpful in feedback
- Risk-aware but solution-focused
- Quality-driven with high standards
- Collaborative with PM Agent

Quality Standards:
- Technical feasibility must be realistic
- Acceptance criteria must be testable and complete
- Dependencies must be identified and addressed
- Implementation approach must be sound
- Overall quality score must be ≥ 0.8 for approval
"""


# Export the Tech Lead Agent class
__all__ = ["TechLeadAgent"]