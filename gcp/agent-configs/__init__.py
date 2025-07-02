#!/usr/bin/env python3

"""
PM Jira Agent Multi-Agent System
High-quality Jira ticket creation through intelligent multi-agent workflows
"""

from .orchestrator import MultiAgentOrchestrator, create_jira_ticket_with_ai
from .pm_agent import PMAgent
from .tech_lead_agent import TechLeadAgent
from .jira_agent import JiraCreatorAgent
from .tools import CloudFunctionTools, QualityGates

__version__ = "0.2.0"
__author__ = "PM Jira Agent System"
__description__ = "AI-powered multi-agent system for creating high-quality Jira tickets"

# Main entry points
__all__ = [
    # Main orchestrator
    "MultiAgentOrchestrator",
    "create_jira_ticket_with_ai",
    
    # Individual agents
    "PMAgent",
    "TechLeadAgent", 
    "JiraCreatorAgent",
    
    # Tools and utilities
    "CloudFunctionTools",
    "QualityGates"
]

# Package metadata
PACKAGE_INFO = {
    "name": "pm-jira-agent",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "phase": "Phase 2 - Multi-Agent Implementation",
    "status": "Development Complete",
    "agents": {
        "pm_agent": "Product Manager analysis and ticket drafting",
        "tech_lead_agent": "Technical review and quality validation", 
        "jira_creator_agent": "Final ticket creation and execution",
        "orchestrator": "Multi-agent workflow coordination"
    },
    "integrations": {
        "gitbook_api": "https://gitbook-api-jlhinciqia-od.a.run.app",
        "jira_api": "https://jira-api-jlhinciqia-od.a.run.app",
        "vertex_ai": "google-cloud-aiplatform",
        "gcp_project": "service-execution-uat-bb7"
    },
    "quality_features": {
        "quality_threshold": 0.8,
        "max_iterations": 3,
        "multi_agent_review": True,
        "gitbook_integration": True,
        "jira_patterns_analysis": True,
        "comprehensive_scoring": True
    }
}