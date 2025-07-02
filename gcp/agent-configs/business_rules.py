#!/usr/bin/env python3

"""
Advanced Business Rules Engine - Phase 3
Implements sophisticated business logic and automation rules for ticket creation
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class Priority(Enum):
    """Ticket priority levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class IssueType(Enum):
    """Jira issue types"""
    STORY = "Story"
    TASK = "Task"
    BUG = "Bug"
    EPIC = "Epic"
    SUBTASK = "Sub-task"

class BusinessRuleCategory(Enum):
    """Categories of business rules"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    INTEGRATION = "integration"
    UI_UX = "ui_ux"
    DATA = "data"
    GENERAL = "general"

class BusinessRulesEngine:
    """Advanced business rules engine for intelligent ticket processing"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
        self.templates = self._initialize_templates()
        self.approval_workflows = self._initialize_approval_workflows()
        
        logger.info("Business Rules Engine initialized with advanced rule sets")
    
    def apply_business_rules(self, ticket_draft: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply comprehensive business rules to ticket draft
        
        Args:
            ticket_draft: Initial ticket draft
            context: Additional context information
            
        Returns:
            Enhanced ticket draft with business rules applied
        """
        try:
            logger.info("Applying business rules to ticket draft")
            
            # Step 1: Analyze ticket content
            content_analysis = self._analyze_ticket_content(ticket_draft)
            
            # Step 2: Apply domain-specific rules
            rule_results = self._apply_domain_rules(ticket_draft, content_analysis)
            
            # Step 3: Enhance with templates
            template_enhancements = self._apply_templates(ticket_draft, content_analysis)
            
            # Step 4: Determine approval workflow
            approval_workflow = self._determine_approval_workflow(ticket_draft, rule_results)
            
            # Step 5: Apply automatic enhancements
            enhanced_ticket = self._apply_automatic_enhancements(
                ticket_draft, rule_results, template_enhancements
            )
            
            return {
                "success": True,
                "enhanced_ticket": enhanced_ticket,
                "rule_results": rule_results,
                "content_analysis": content_analysis,
                "approval_workflow": approval_workflow,
                "template_applied": template_enhancements.get("template_name"),
                "business_rules_applied": True
            }
            
        except Exception as e:
            logger.error(f"Error applying business rules: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "enhanced_ticket": ticket_draft  # Return original on error
            }
    
    def validate_compliance(self, ticket_draft: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate ticket against compliance requirements
        
        Args:
            ticket_draft: Ticket to validate
            
        Returns:
            Compliance validation results
        """
        validation_results = {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # GDPR compliance check
        gdpr_check = self._check_gdpr_compliance(ticket_draft)
        if not gdpr_check["compliant"]:
            validation_results["violations"].extend(gdpr_check["violations"])
            validation_results["compliant"] = False
        
        # Security compliance check
        security_check = self._check_security_compliance(ticket_draft)
        if not security_check["compliant"]:
            validation_results["violations"].extend(security_check["violations"])
            validation_results["compliant"] = False
        
        # Accessibility compliance check
        accessibility_check = self._check_accessibility_compliance(ticket_draft)
        if accessibility_check["warnings"]:
            validation_results["warnings"].extend(accessibility_check["warnings"])
        
        return validation_results
    
    def _analyze_ticket_content(self, ticket_draft: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ticket content for rule application"""
        
        summary = ticket_draft.get("summary", "").lower()
        description = ticket_draft.get("description", "").lower()
        full_text = f"{summary} {description}"
        
        analysis = {
            "categories": [],
            "complexity": "medium",
            "risk_level": "low",
            "keywords": [],
            "estimated_effort": "TBD",
            "integration_points": [],
            "security_implications": False,
            "data_privacy_implications": False,
            "ui_changes": False,
            "api_changes": False,
            "database_changes": False
        }
        
        # Category detection
        category_keywords = {
            BusinessRuleCategory.SECURITY: ["security", "authentication", "authorization", "permission", "access", "login", "password", "encryption", "ssl", "tls"],
            BusinessRuleCategory.PERFORMANCE: ["performance", "optimization", "speed", "latency", "caching", "memory", "cpu", "load", "scale"],
            BusinessRuleCategory.COMPLIANCE: ["gdpr", "privacy", "audit", "compliance", "regulation", "policy", "legal"],
            BusinessRuleCategory.INTEGRATION: ["api", "integration", "webhook", "external", "third-party", "service", "connector"],
            BusinessRuleCategory.UI_UX: ["ui", "ux", "interface", "design", "user experience", "frontend", "styling", "layout"],
            BusinessRuleCategory.DATA: ["database", "data", "migration", "schema", "table", "query", "storage"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in full_text for keyword in keywords):
                analysis["categories"].append(category.value)
        
        # Complexity assessment
        complexity_indicators = {
            "high": ["migration", "refactor", "architecture", "integration", "performance", "security"],
            "medium": ["feature", "enhancement", "update", "modify", "extend"],
            "low": ["fix", "bug", "typo", "text", "styling", "minor"]
        }
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in full_text for indicator in indicators):
                analysis["complexity"] = complexity
                break
        
        # Risk assessment
        high_risk_keywords = ["database", "security", "authentication", "payment", "external", "migration"]
        medium_risk_keywords = ["api", "integration", "performance", "data"]
        
        if any(keyword in full_text for keyword in high_risk_keywords):
            analysis["risk_level"] = "high"
        elif any(keyword in full_text for keyword in medium_risk_keywords):
            analysis["risk_level"] = "medium"
        
        # Specific implications
        analysis["security_implications"] = any(keyword in full_text for keyword in ["security", "auth", "permission", "access"])
        analysis["data_privacy_implications"] = any(keyword in full_text for keyword in ["data", "privacy", "personal", "gdpr"])
        analysis["ui_changes"] = any(keyword in full_text for keyword in ["ui", "interface", "frontend", "design"])
        analysis["api_changes"] = any(keyword in full_text for keyword in ["api", "endpoint", "service"])
        analysis["database_changes"] = any(keyword in full_text for keyword in ["database", "schema", "table", "migration"])
        
        return analysis
    
    def _apply_domain_rules(self, ticket_draft: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply domain-specific business rules"""
        
        rule_results = {
            "rules_applied": [],
            "priority_adjustments": [],
            "label_additions": [],
            "component_assignments": [],
            "validation_requirements": [],
            "testing_requirements": [],
            "documentation_requirements": []
        }
        
        categories = analysis.get("categories", [])
        
        # Security rules
        if BusinessRuleCategory.SECURITY.value in categories:
            rule_results["rules_applied"].append("security_rules")
            rule_results["priority_adjustments"].append("Elevated to High priority due to security implications")
            rule_results["label_additions"].extend(["security", "security-review-required"])
            rule_results["validation_requirements"].extend([
                "Security team review required",
                "Penetration testing required",
                "Security documentation update required"
            ])
            rule_results["testing_requirements"].extend([
                "Security test suite execution",
                "Authentication flow testing",
                "Authorization boundary testing"
            ])
        
        # Performance rules
        if BusinessRuleCategory.PERFORMANCE.value in categories:
            rule_results["rules_applied"].append("performance_rules")
            rule_results["label_additions"].extend(["performance", "optimization"])
            rule_results["validation_requirements"].extend([
                "Performance benchmarking required",
                "Load testing required"
            ])
            rule_results["testing_requirements"].extend([
                "Performance test suite",
                "Memory usage validation",
                "Response time measurement"
            ])
        
        # Compliance rules
        if BusinessRuleCategory.COMPLIANCE.value in categories:
            rule_results["rules_applied"].append("compliance_rules")
            rule_results["priority_adjustments"].append("Priority reviewed for compliance implications")
            rule_results["label_additions"].extend(["compliance", "audit-trail"])
            rule_results["documentation_requirements"].extend([
                "Compliance documentation update",
                "Audit trail documentation",
                "Privacy impact assessment"
            ])
        
        # Integration rules
        if BusinessRuleCategory.INTEGRATION.value in categories:
            rule_results["rules_applied"].append("integration_rules")
            rule_results["label_additions"].extend(["integration", "external-dependency"])
            rule_results["validation_requirements"].extend([
                "Integration testing required",
                "Fallback mechanism validation",
                "Error handling verification"
            ])
        
        # UI/UX rules
        if BusinessRuleCategory.UI_UX.value in categories:
            rule_results["rules_applied"].append("ui_ux_rules")
            rule_results["label_additions"].extend(["ui", "ux", "frontend"])
            rule_results["validation_requirements"].extend([
                "Design review required",
                "Accessibility testing required",
                "Cross-browser testing required"
            ])
            rule_results["documentation_requirements"].extend([
                "User documentation update",
                "Design system documentation"
            ])
        
        # Data rules
        if BusinessRuleCategory.DATA.value in categories:
            rule_results["rules_applied"].append("data_rules")
            rule_results["label_additions"].extend(["data", "database"])
            rule_results["validation_requirements"].extend([
                "Database migration testing",
                "Data integrity validation",
                "Backup and recovery testing"
            ])
        
        # Risk-based adjustments
        if analysis.get("risk_level") == "high":
            rule_results["priority_adjustments"].append("High risk - consider priority elevation")
            rule_results["validation_requirements"].extend([
                "Additional review cycles required",
                "Stakeholder approval required"
            ])
        
        return rule_results
    
    def _apply_templates(self, ticket_draft: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply appropriate templates based on content analysis"""
        
        categories = analysis.get("categories", [])
        
        # Select best matching template
        template_name = None
        template_enhancements = {}
        
        if BusinessRuleCategory.SECURITY.value in categories:
            template_name = "security_feature"
        elif BusinessRuleCategory.INTEGRATION.value in categories:
            template_name = "api_integration"
        elif BusinessRuleCategory.UI_UX.value in categories:
            template_name = "ui_enhancement"
        elif BusinessRuleCategory.DATA.value in categories:
            template_name = "data_feature"
        else:
            template_name = "standard_feature"
        
        if template_name and template_name in self.templates:
            template = self.templates[template_name]
            template_enhancements = {
                "template_name": template_name,
                "acceptance_criteria_additions": template.get("acceptance_criteria", []),
                "testing_checklist": template.get("testing_checklist", []),
                "documentation_requirements": template.get("documentation", []),
                "definition_of_done": template.get("definition_of_done", [])
            }
        
        return template_enhancements
    
    def _determine_approval_workflow(self, ticket_draft: Dict[str, Any], rule_results: Dict[str, Any]) -> Dict[str, Any]:
        """Determine appropriate approval workflow"""
        
        priority = ticket_draft.get("priority", "Medium")
        labels = rule_results.get("label_additions", [])
        
        workflow = {
            "workflow_type": "standard",
            "approvers": [],
            "review_stages": [],
            "estimated_approval_time": "1-2 days"
        }
        
        # Security workflow
        if "security" in labels:
            workflow.update({
                "workflow_type": "security_enhanced",
                "approvers": ["Tech Lead", "Security Team", "Product Owner"],
                "review_stages": ["Technical Review", "Security Review", "Business Approval"],
                "estimated_approval_time": "3-5 days"
            })
        
        # High priority workflow
        elif priority in [Priority.CRITICAL.value, Priority.HIGH.value]:
            workflow.update({
                "workflow_type": "expedited",
                "approvers": ["Tech Lead", "Product Owner"],
                "review_stages": ["Technical Review", "Business Approval"],
                "estimated_approval_time": "1 day"
            })
        
        # Integration workflow
        elif "integration" in labels:
            workflow.update({
                "workflow_type": "integration_review",
                "approvers": ["Tech Lead", "Architecture Team", "Product Owner"],
                "review_stages": ["Technical Review", "Architecture Review", "Business Approval"],
                "estimated_approval_time": "2-3 days"
            })
        
        return workflow
    
    def _apply_automatic_enhancements(self, ticket_draft: Dict[str, Any], 
                                    rule_results: Dict[str, Any], 
                                    template_enhancements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply automatic enhancements to ticket"""
        
        enhanced_ticket = ticket_draft.copy()
        
        # Priority adjustments
        if rule_results.get("priority_adjustments"):
            if "security" in rule_results.get("label_additions", []):
                enhanced_ticket["priority"] = Priority.HIGH.value
        
        # Label additions
        existing_labels = enhanced_ticket.get("labels", [])
        new_labels = existing_labels + rule_results.get("label_additions", [])
        enhanced_ticket["labels"] = list(set(new_labels))  # Remove duplicates
        
        # Component assignments
        components = rule_results.get("component_assignments", [])
        if components:
            enhanced_ticket["components"] = components
        
        # Enhanced description with requirements
        description = enhanced_ticket.get("description", "")
        
        # Add validation requirements
        validation_reqs = rule_results.get("validation_requirements", [])
        if validation_reqs:
            description += "\n\n## Validation Requirements\n"
            for req in validation_reqs:
                description += f"- {req}\n"
        
        # Add testing requirements
        testing_reqs = rule_results.get("testing_requirements", [])
        template_testing = template_enhancements.get("testing_checklist", [])
        all_testing_reqs = testing_reqs + template_testing
        
        if all_testing_reqs:
            description += "\n\n## Testing Requirements\n"
            for req in all_testing_reqs:
                description += f"- {req}\n"
        
        # Add documentation requirements
        doc_reqs = rule_results.get("documentation_requirements", [])
        template_docs = template_enhancements.get("documentation_requirements", [])
        all_doc_reqs = doc_reqs + template_docs
        
        if all_doc_reqs:
            description += "\n\n## Documentation Requirements\n"
            for req in all_doc_reqs:
                description += f"- {req}\n"
        
        # Add definition of done
        dod = template_enhancements.get("definition_of_done", [])
        if dod:
            description += "\n\n## Definition of Done\n"
            for item in dod:
                description += f"- {item}\n"
        
        enhanced_ticket["description"] = description
        
        return enhanced_ticket
    
    def _check_gdpr_compliance(self, ticket_draft: Dict[str, Any]) -> Dict[str, Any]:
        """Check GDPR compliance"""
        
        summary = ticket_draft.get("summary", "").lower()
        description = ticket_draft.get("description", "").lower()
        full_text = f"{summary} {description}"
        
        violations = []
        
        # Check for personal data handling
        personal_data_keywords = ["personal data", "user data", "customer data", "email", "phone", "address"]
        if any(keyword in full_text for keyword in personal_data_keywords):
            if "privacy" not in full_text and "gdpr" not in full_text:
                violations.append("Personal data handling detected without GDPR considerations")
        
        # Check for data processing activities
        processing_keywords = ["collect", "store", "process", "analyze", "share"]
        if any(keyword in full_text for keyword in processing_keywords):
            if "consent" not in full_text and "lawful basis" not in full_text:
                violations.append("Data processing activity without consent or lawful basis consideration")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations
        }
    
    def _check_security_compliance(self, ticket_draft: Dict[str, Any]) -> Dict[str, Any]:
        """Check security compliance"""
        
        summary = ticket_draft.get("summary", "").lower()
        description = ticket_draft.get("description", "").lower()
        full_text = f"{summary} {description}"
        
        violations = []
        
        # Check for authentication/authorization
        auth_keywords = ["login", "authentication", "authorization", "access control"]
        if any(keyword in full_text for keyword in auth_keywords):
            if "security review" not in full_text:
                violations.append("Authentication/authorization changes require security review")
        
        # Check for external integrations
        external_keywords = ["external api", "third party", "webhook", "integration"]
        if any(keyword in full_text for keyword in external_keywords):
            if "security assessment" not in full_text:
                violations.append("External integrations require security assessment")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations
        }
    
    def _check_accessibility_compliance(self, ticket_draft: Dict[str, Any]) -> Dict[str, Any]:
        """Check accessibility compliance"""
        
        summary = ticket_draft.get("summary", "").lower()
        description = ticket_draft.get("description", "").lower()
        full_text = f"{summary} {description}"
        
        warnings = []
        
        # Check for UI changes
        ui_keywords = ["ui", "interface", "frontend", "design", "layout"]
        if any(keyword in full_text for keyword in ui_keywords):
            if "accessibility" not in full_text and "wcag" not in full_text:
                warnings.append("UI changes should consider accessibility requirements (WCAG 2.1)")
        
        return {
            "warnings": warnings
        }
    
    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize business rules configuration"""
        return {
            "security_rules": {
                "priority_elevation": True,
                "required_reviews": ["security_team"],
                "mandatory_labels": ["security", "security-review-required"],
                "testing_requirements": ["security_testing", "penetration_testing"]
            },
            "performance_rules": {
                "testing_requirements": ["performance_testing", "load_testing"],
                "documentation_requirements": ["performance_benchmarks"]
            },
            "compliance_rules": {
                "documentation_requirements": ["compliance_documentation", "audit_trail"],
                "review_requirements": ["legal_review"]
            }
        }
    
    def _initialize_templates(self) -> Dict[str, Any]:
        """Initialize ticket templates"""
        return {
            "security_feature": {
                "acceptance_criteria": [
                    "Security review completed and approved",
                    "Authentication mechanisms tested",
                    "Authorization boundaries validated",
                    "Security documentation updated"
                ],
                "testing_checklist": [
                    "Security test suite execution",
                    "Penetration testing completed",
                    "Authentication flow testing",
                    "Data encryption validation"
                ],
                "documentation": [
                    "Security architecture documentation",
                    "Threat model update",
                    "Security configuration guide"
                ],
                "definition_of_done": [
                    "Code review completed",
                    "Security review passed",
                    "All tests passing",
                    "Documentation updated",
                    "Deployed to production"
                ]
            },
            "api_integration": {
                "acceptance_criteria": [
                    "API integration functional and tested",
                    "Error handling implemented",
                    "Rate limiting considered",
                    "API documentation updated"
                ],
                "testing_checklist": [
                    "Integration testing completed",
                    "Error scenario testing",
                    "Performance testing",
                    "Fallback mechanism testing"
                ],
                "documentation": [
                    "API integration documentation",
                    "Error handling guide",
                    "Monitoring setup documentation"
                ]
            },
            "ui_enhancement": {
                "acceptance_criteria": [
                    "UI changes implemented according to design",
                    "Accessibility requirements met",
                    "Cross-browser compatibility verified",
                    "User experience validated"
                ],
                "testing_checklist": [
                    "Visual regression testing",
                    "Accessibility testing (WCAG 2.1)",
                    "Cross-browser testing",
                    "Mobile responsiveness testing"
                ],
                "documentation": [
                    "User interface documentation",
                    "Design system updates",
                    "User guide updates"
                ]
            },
            "data_feature": {
                "acceptance_criteria": [
                    "Data model changes implemented",
                    "Migration scripts tested",
                    "Data integrity validated",
                    "Backup and recovery tested"
                ],
                "testing_checklist": [
                    "Database migration testing",
                    "Data integrity validation",
                    "Performance impact testing",
                    "Backup and recovery testing"
                ],
                "documentation": [
                    "Database schema documentation",
                    "Migration procedure documentation",
                    "Data handling documentation"
                ]
            },
            "standard_feature": {
                "acceptance_criteria": [
                    "Feature implemented according to requirements",
                    "All edge cases handled",
                    "Testing completed successfully",
                    "Documentation updated"
                ],
                "testing_checklist": [
                    "Unit testing completed",
                    "Integration testing completed",
                    "End-to-end testing completed",
                    "Manual testing completed"
                ],
                "documentation": [
                    "Feature documentation",
                    "User guide updates",
                    "Technical documentation"
                ]
            }
        }
    
    def _initialize_approval_workflows(self) -> Dict[str, Any]:
        """Initialize approval workflow configurations"""
        return {
            "standard": {
                "stages": ["technical_review", "business_approval"],
                "approvers": ["tech_lead", "product_owner"],
                "estimated_time": "1-2 days"
            },
            "security_enhanced": {
                "stages": ["technical_review", "security_review", "business_approval"],
                "approvers": ["tech_lead", "security_team", "product_owner"],
                "estimated_time": "3-5 days"
            },
            "expedited": {
                "stages": ["combined_review"],
                "approvers": ["tech_lead", "product_owner"],
                "estimated_time": "1 day"
            }
        }


# Export the Business Rules Engine
__all__ = ["BusinessRulesEngine", "Priority", "IssueType", "BusinessRuleCategory"]