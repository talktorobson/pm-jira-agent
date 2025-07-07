#!/usr/bin/env python3

"""
Custom Tools for PM Jira Agent Multi-Agent System
Integrates with Cloud Functions for GitBook and Jira APIs
Uses internal GCP service-to-service authentication
"""

import requests
import json
from typing import Dict, List, Any, Optional
from google.cloud import secretmanager
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import google.auth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudFunctionTools:
    """Tools that integrate with deployed Cloud Functions using internal GCP authentication"""
    
    def __init__(self, project_id: str = "service-execution-uat-bb7"):
        self.project_id = project_id
        self.gitbook_function_url = "https://gitbook-api-jlhinciqia-od.a.run.app"
        self.jira_function_url = "https://jira-api-jlhinciqia-od.a.run.app"
        
        # Initialize GCP internal authentication
        self.credentials = None
        self._setup_internal_auth()
    
    def _setup_internal_auth(self):
        """Setup internal GCP service-to-service authentication"""
        try:
            # Use default credentials (works in Vertex AI environment)
            credentials, project = google.auth.default()
            self.credentials = credentials
            logger.info(f"✅ Internal GCP authentication initialized for project: {project}")
        except Exception as e:
            logger.warning(f"⚠️  Internal auth not available: {e}")
            self.credentials = None
    
    def _get_internal_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for internal GCP service calls"""
        headers = {"Content-Type": "application/json"}
        
        if self.credentials:
            try:
                # Refresh credentials if needed
                if not self.credentials.valid:
                    self.credentials.refresh(Request())
                
                # Add authorization header for internal calls
                headers["Authorization"] = f"Bearer {self.credentials.token}"
                logger.debug("✅ Using internal GCP service authentication")
            except Exception as e:
                logger.warning(f"⚠️  Failed to get internal auth token: {e}")
        else:
            logger.info("ℹ️  No internal auth available, using unauthenticated call")
        
        return headers
    
    def search_gitbook_content(self, query: str) -> Dict[str, Any]:
        """
        Search GitBook documentation for relevant context
        
        Args:
            query: Search query for GitBook content
            
        Returns:
            Dictionary containing search results and content
        """
        try:
            payload = {
                "action": "get_content",
                "query": query
            }
            
            # Use internal GCP authentication for service-to-service calls
            headers = self._get_internal_auth_headers()
            
            response = requests.post(
                self.gitbook_function_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"GitBook search successful for query: {query}")
                return {
                    "success": True,
                    "content": result.get("content", ""),
                    "space_info": result.get("raw_data", {}),
                    "source": "GitBook: [SSI] Service Sales Integration"
                }
            else:
                logger.error(f"GitBook API error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"GitBook API error: {response.status_code}",
                    "content": ""
                }
                
        except Exception as e:
            logger.error(f"GitBook search error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }
    
    def analyze_existing_jira_tickets(self, project_key: str = "AHSSI", max_results: int = 10) -> Dict[str, Any]:
        """
        Analyze existing Jira tickets for context and patterns
        
        Args:
            project_key: Jira project key (default: AHSSI)
            max_results: Maximum number of tickets to analyze
            
        Returns:
            Dictionary containing ticket analysis and patterns
        """
        try:
            payload = {
                "action": "get_tickets",
                "jql": f"project = {project_key} ORDER BY created DESC",
                "max_results": max_results
            }
            
            # Use internal GCP authentication for service-to-service calls
            headers = self._get_internal_auth_headers()
            
            response = requests.post(
                self.jira_function_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                tickets = result.get("data", {}).get("issues", [])
                
                # Analyze patterns
                analysis = self._analyze_ticket_patterns(tickets)
                
                logger.info(f"Analyzed {len(tickets)} Jira tickets")
                return {
                    "success": True,
                    "ticket_count": len(tickets),
                    "tickets": tickets[:5],  # Return top 5 for context
                    "patterns": analysis,
                    "project": project_key
                }
            else:
                logger.error(f"Jira API error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Jira API error: {response.status_code}",
                    "tickets": []
                }
                
        except Exception as e:
            logger.error(f"Jira analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tickets": []
            }
    
    def create_jira_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Jira ticket after quality validation
        
        Args:
            ticket_data: Dictionary containing ticket information
            
        Returns:
            Dictionary containing creation result and ticket details
        """
        try:
            # Ensure required fields are present
            required_fields = ["summary", "description"]
            for field in required_fields:
                if field not in ticket_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}",
                        "ticket_key": None
                    }
            
            payload = {
                "action": "create_ticket",
                "ticket_data": {
                    "summary": ticket_data["summary"],
                    "description": ticket_data["description"],
                    "issue_type": ticket_data.get("issue_type", "Story"),
                    "priority": ticket_data.get("priority", "Medium"),
                    "labels": ticket_data.get("labels", ["ai-generated", "pm-agent"]),
                    "components": ticket_data.get("components", [])
                }
            }
            
            # Use internal GCP authentication for service-to-service calls
            headers = self._get_internal_auth_headers()
            
            response = requests.post(
                self.jira_function_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                ticket_key = result.get("data", {}).get("key", "Unknown")
                
                logger.info(f"Jira ticket created successfully: {ticket_key}")
                return {
                    "success": True,
                    "ticket_key": ticket_key,
                    "ticket_url": f"https://jira.adeo.com/browse/{ticket_key}",
                    "data": result.get("data", {})
                }
            else:
                logger.error(f"Jira creation error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Jira creation error: {response.status_code}",
                    "ticket_key": None
                }
                
        except Exception as e:
            logger.error(f"Jira creation error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "ticket_key": None
            }
    
    def _analyze_ticket_patterns(self, tickets: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in existing tickets for context"""
        if not tickets:
            return {"patterns": "No tickets available for analysis"}
        
        # Extract patterns
        issue_types = {}
        priorities = {}
        components = set()
        common_labels = set()
        
        for ticket in tickets:
            fields = ticket.get("fields", {})
            
            # Issue types
            issue_type = fields.get("issuetype", {}).get("name", "Unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            # Priorities  
            priority = fields.get("priority", {}).get("name", "Unknown")
            priorities[priority] = priorities.get(priority, 0) + 1
            
            # Components
            for comp in fields.get("components", []):
                components.add(comp.get("name", ""))
            
            # Labels
            for label in fields.get("labels", []):
                common_labels.add(label)
        
        return {
            "most_common_issue_type": max(issue_types.items(), key=lambda x: x[1])[0] if issue_types else "Story",
            "most_common_priority": max(priorities.items(), key=lambda x: x[1])[0] if priorities else "Medium",
            "available_components": list(components)[:5],  # Top 5 components
            "common_labels": list(common_labels)[:10],  # Top 10 labels
            "total_tickets_analyzed": len(tickets)
        }


class QualityGates:
    """Quality assessment and scoring tools"""
    
    @staticmethod
    def calculate_quality_score(ticket_draft: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive quality score for ticket draft
        
        Args:
            ticket_draft: Dictionary containing ticket information
            
        Returns:
            Dictionary with detailed scoring breakdown
        """
        scores = {}
        
        # 1. Summary Clarity (0-1)
        summary = ticket_draft.get("summary", "")
        summary_score = QualityGates._score_summary_clarity(summary)
        scores["summary_clarity"] = summary_score
        
        # 2. User Story Format (0-1)
        description = ticket_draft.get("description", "")
        user_story_score = QualityGates._score_user_story_format(description)
        scores["user_story_format"] = user_story_score
        
        # 3. Acceptance Criteria Completeness (0-1)
        acceptance_criteria_score = QualityGates._score_acceptance_criteria(description)
        scores["acceptance_criteria"] = acceptance_criteria_score
        
        # 4. Technical Feasibility (0-1)
        technical_score = QualityGates._score_technical_feasibility(ticket_draft)
        scores["technical_feasibility"] = technical_score
        
        # 5. Business Value (0-1)
        business_score = QualityGates._score_business_value(ticket_draft)
        scores["business_value"] = business_score
        
        # Calculate overall score (weighted average)
        weights = {
            "summary_clarity": 0.15,
            "user_story_format": 0.25,
            "acceptance_criteria": 0.25,
            "technical_feasibility": 0.20,
            "business_value": 0.15
        }
        
        overall_score = sum(scores[key] * weights[key] for key in scores.keys())
        
        return {
            "overall_score": round(overall_score, 2),
            "detailed_scores": scores,
            "weights_used": weights,
            "quality_threshold": 0.8,
            "passes_quality_gate": overall_score >= 0.8,
            "recommendations": QualityGates._generate_recommendations(scores, overall_score)
        }
    
    @staticmethod
    def _score_summary_clarity(summary: str) -> float:
        """Score summary clarity (0-1)"""
        if not summary:
            return 0.0
        
        score = 0.0
        
        # Length check (10-80 characters is optimal)
        if 10 <= len(summary) <= 80:
            score += 0.4
        elif len(summary) > 5:
            score += 0.2
        
        # Contains action verb
        action_verbs = ["add", "create", "update", "fix", "implement", "improve", "refactor", "remove"]
        if any(verb in summary.lower() for verb in action_verbs):
            score += 0.3
        
        # Clear and specific (not too generic)
        generic_words = ["something", "stuff", "thing", "issue", "problem"]
        if not any(word in summary.lower() for word in generic_words):
            score += 0.3
        
        return min(score, 1.0)
    
    @staticmethod
    def _score_user_story_format(description: str) -> float:
        """Score user story format (0-1)"""
        if not description:
            return 0.0
        
        desc_lower = description.lower()
        score = 0.0
        
        # Check for "As a" format
        if "as a" in desc_lower or "as an" in desc_lower:
            score += 0.4
        
        # Check for "I want" or "I need"
        if "i want" in desc_lower or "i need" in desc_lower:
            score += 0.3
        
        # Check for "so that" (benefit)
        if "so that" in desc_lower or "in order to" in desc_lower:
            score += 0.3
        
        return min(score, 1.0)
    
    @staticmethod
    def _score_acceptance_criteria(description: str) -> float:
        """Score acceptance criteria completeness (0-1)"""
        if not description:
            return 0.0
        
        desc_lower = description.lower()
        score = 0.0
        
        # Look for acceptance criteria section
        ac_indicators = ["acceptance criteria", "given", "when", "then", "should", "criteria"]
        if any(indicator in desc_lower for indicator in ac_indicators):
            score += 0.5
        
        # Count bullet points or numbered lists (indicates multiple criteria)
        bullet_count = description.count("•") + description.count("-") + description.count("*")
        number_count = sum(1 for line in description.split("\n") if line.strip() and line.strip()[0].isdigit())
        
        criteria_count = bullet_count + number_count
        if criteria_count >= 3:
            score += 0.5
        elif criteria_count >= 1:
            score += 0.3
        
        return min(score, 1.0)
    
    @staticmethod
    def _score_technical_feasibility(ticket_draft: Dict[str, Any]) -> float:
        """Score technical feasibility (0-1)"""
        # Basic scoring - can be enhanced with ML model
        score = 0.7  # Default reasonable score
        
        # Check for unrealistic expectations
        description = ticket_draft.get("description", "").lower()
        summary = ticket_draft.get("summary", "").lower()
        
        unrealistic_terms = ["immediately", "asap", "urgent", "overnight", "quick fix"]
        if any(term in description + summary for term in unrealistic_terms):
            score -= 0.2
        
        # Check for proper scope
        if len(ticket_draft.get("description", "")) > 100:  # Detailed description suggests good planning
            score += 0.2
        
        return max(min(score, 1.0), 0.1)  # Keep between 0.1 and 1.0
    
    @staticmethod
    def _score_business_value(ticket_draft: Dict[str, Any]) -> float:
        """Score business value (0-1)"""
        # Basic scoring - can be enhanced with business rules
        score = 0.6  # Default reasonable score
        
        description = ticket_draft.get("description", "").lower()
        summary = ticket_draft.get("summary", "").lower()
        
        # Look for business value indicators
        value_indicators = ["user", "customer", "revenue", "efficiency", "productivity", "experience"]
        if any(indicator in description + summary for indicator in value_indicators):
            score += 0.3
        
        # Check for measurable outcomes
        measurable_terms = ["increase", "decrease", "improve", "reduce", "faster", "better"]
        if any(term in description + summary for term in measurable_terms):
            score += 0.1
        
        return min(score, 1.0)
    
    @staticmethod
    def _generate_recommendations(scores: Dict[str, float], overall_score: float) -> List[str]:
        """Generate improvement recommendations based on scores"""
        recommendations = []
        
        if scores["summary_clarity"] < 0.7:
            recommendations.append("Improve summary clarity with action verbs and specific details")
        
        if scores["user_story_format"] < 0.7:
            recommendations.append("Use proper user story format: 'As a [user] I want [goal] so that [benefit]'")
        
        if scores["acceptance_criteria"] < 0.7:
            recommendations.append("Add detailed acceptance criteria with at least 3 testable conditions")
        
        if scores["technical_feasibility"] < 0.7:
            recommendations.append("Review technical approach and ensure realistic scope")
        
        if scores["business_value"] < 0.7:
            recommendations.append("Clarify business value and user impact")
        
        if overall_score < 0.8:
            recommendations.append("Overall quality below threshold (0.8) - address above recommendations")
        
        return recommendations if recommendations else ["Ticket meets quality standards!"]


# Export main classes
__all__ = ["CloudFunctionTools", "QualityGates"]