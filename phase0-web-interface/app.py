#!/usr/bin/env python3
"""
PM Jira Agent - Phase 0 Web Interface
Simple Flask application for individual PM instances
"""

import os
import sys
import json
import yaml
import uuid
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import logging

# Import enhanced orchestrator
try:
    from enhanced_orchestrator import create_jira_ticket_with_ai
    print("Enhanced orchestrator imported successfully")
except ImportError as e:
    print(f"Warning: Could not import enhanced orchestrator: {e}")
    create_jira_ticket_with_ai = None

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for tracking workflows
active_workflows = {}

def load_user_config():
    """Load user configuration from config.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
    default_config = {
        'user_info': {
            'name': 'Robson Reis',
            'email': 'robson.reis@adeo.com',
            'team': 'AHS SSI Team'
        },
        'jira': {
            'base_url': 'https://jira.adeo.com',
            'project_key': 'AHSSI',
            'default_issue_type': 'Story',
            'default_priority': 'Medium'
        },
        'gitbook': {
            'enabled': True,
            'space_id': 'https://app.gitbook.com/o/0gRlAkSocTvnN36NTnDZ/s/Jw57BieQciFYoCHgwVlm/'
        },
        'custom_prompts': {
            'company_context': 'We are services sales integrator to home services execution management platform. We part of a DIY retailer, Leroy Merlin, which sells products with installations of them. For each installation sold with product, we create a service execution order into AHS (Adeo Home Services Platform). Our product is responsible to get this service sales order and integrate it into AHS to create this service execution order to be managed during its installation service execution.',
            'writing_style': 'professional',
            'stakeholder_mapping': {
                'Security Team': 'security@company.com',
                'UX Team': 'ux@company.com',
                'Engineering': 'dev@company.com',
                'QA Team': 'qa@company.com'
            }
        },
        'business_rules': {
            'ui_ux_guidelines': 'Follow modern UI/UX best practices and accessibility standards',
            'security_requirements': 'All user data must be secured and encrypted. Follow OWASP guidelines.',
            'performance_standards': 'Optimize for fast user experience. Page load times should be under 3 seconds.'
        },
        'agent_prompts': {
            'pm_agent_basic': '''You are an expert Product Manager creating JIRA tickets. 

User Request: {user_request}

Additional Context from GitBook: {gitbook_context}

Create a comprehensive JIRA ticket with:
1. Clear, actionable summary (max 100 characters)
2. Detailed description with business context
3. Specific acceptance criteria (3-5 bullet points)
4. Technical considerations
5. Definition of Done

Format your response as JSON:
{
  "summary": "Brief ticket title",
  "description": "Detailed description with context",
  "acceptance_criteria": ["Criterion 1", "Criterion 2", "Criterion 3"],
  "technical_notes": "Any technical considerations",
  "definition_of_done": "Clear completion criteria"
}''',
            'pm_agent_enhanced': '''You are an expert Product Manager with access to company documentation and historical JIRA tickets. 

**User Request:** "{user_request}"
**Priority:** {priority}
**Component:** {component}
**Issue Type:** {issue_type}
{context_summary}
{gitbook_context}
{similar_tickets_context}

**TASK:** Create a professional JIRA ticket with enhanced formatting that leverages the research context above. Reference specific documentation or similar ticket patterns where relevant.

**SUMMARY REQUIREMENTS:**
- Start with action verb (Implement, Fix, Create, Update, Add, Enhance, etc.)
- Be specific and descriptive (50-150 characters)
- Action-oriented and meaningful to the content
- Format: "[Action Verb] [specific feature/fix] [context/benefit]"

**DESCRIPTION STRUCTURE (Use exactly this 3-section format with emojis and formatting):**

**🎯 Problem or Opportunity**
*Brief description of the current issue, gap, or opportunity that needs to be addressed*

**⚡ What to Do**
*Clear description of what needs to be built, fixed, or developed with specific requirements*

**🧪 How to Test It**
*Detailed testing instructions with scenarios and expected outcomes*

**LABELS GENERATION:**
Research similar tickets in the project and generate 3-5 relevant labels based on:
- Technology stack (frontend, backend, api, mobile, etc.)
- Feature area (authentication, integration, performance, etc.) 
- Ticket type (enhancement, bug-fix, new-feature, etc.)

**FORMATTING RULES:**
- Use Atlassian/Jira wiki markup syntax
- Use *bold* for section headers and important terms
- Use bullet points with - for lists
- Use emojis strategically for visual appeal
- Keep sections concise but comprehensive

IMPORTANT: Format response as clean JSON (no markdown blocks):
{
    "summary": "Action-oriented summary starting with verb and describing specific outcome",
    "description": "Formatted description using the 3-section structure with emojis, bold headers, and proper Jira markup",
    "acceptance_criteria": ["🎯 Specific testable criterion with clear success definition", "⚡ Another measurable criterion with expected behavior", "🧪 Validation criterion with testing approach"],
    "business_value": "Quantifiable business impact with metrics and strategic alignment",
    "technical_considerations": "Implementation approach with architectural decisions and technical requirements",
    "estimated_complexity": "Low/Medium/High based on technical scope and dependencies",
    "dependencies": ["Technical dependency 1", "Business dependency 2"],
    "risk_assessment": "Key technical and business risks with mitigation strategies",
    "labels": ["label1", "label2", "label3", "label4", "label5"],
    "component": "{component}",
    "priority": "{priority}"
}''',
            'tech_lead_basic': '''You are a Senior Tech Lead reviewing a JIRA ticket for quality and completeness.

Ticket Draft:
Summary: {ticket_draft.get('summary', '')}
Description: {ticket_draft.get('description', '')}
Acceptance Criteria: {ticket_draft.get('acceptance_criteria', [])}

Rate this ticket on 5 dimensions (0.0 to 1.0 each):
1. Summary Clarity: Is the summary clear and actionable?
2. User Story Format: Does it follow proper user story structure?
3. Acceptance Criteria: Are they specific, measurable, and testable?
4. Technical Feasibility: Is the request technically sound?
5. Business Value: Is the business value clear?

Also provide:
- Overall quality score (average of 5 dimensions)
- Specific feedback for improvements
- Technical considerations and risks
- Approval recommendation (approve/needs_improvement)

Format as JSON:
{
  "scores": {
    "summary_clarity": 0.8,
    "user_story_format": 0.7,
    "acceptance_criteria": 0.9,
    "technical_feasibility": 0.8,
    "business_value": 0.7
  },
  "overall_score": 0.78,
  "feedback": "Specific improvement suggestions",
  "technical_notes": "Technical considerations",
  "recommendation": "approve" or "needs_improvement",
  "risks": ["Risk 1", "Risk 2"]
}''',
            'tech_lead_enhanced': '''You are a Senior Tech Lead and Software Architect with deep knowledge of company systems and implementation patterns.

Review this JIRA ticket for quality, technical feasibility, and alignment with company standards:

**Ticket to Review:**
Summary: {ticket_draft.get('summary', 'N/A')}
Description: {ticket_draft.get('description', 'N/A')}
Acceptance Criteria: {ticket_draft.get('acceptance_criteria', [])}
Business Value: {ticket_draft.get('business_value', 'N/A')}
Technical Considerations: {ticket_draft.get('technical_considerations', 'N/A')}
Estimated Complexity: {ticket_draft.get('estimated_complexity', 'N/A')}
{technical_context}
{complexity_context}

Based on the technical documentation and implementation patterns from similar tickets, evaluate this ticket on these dimensions (score 0.0-1.0 each):

1. **Summary Clarity**: Is the title clear, specific, and actionable?
2. **User Story Format**: Does it follow proper user story structure and company conventions?
3. **Acceptance Criteria**: Are criteria specific, measurable, testable, and complete?
4. **Technical Feasibility**: Is this technically achievable with current architecture and constraints?
5. **Business Value**: Is the business impact clearly articulated and measurable?
6. **Architectural Alignment**: Does this align with company technical standards and patterns?
7. **Implementation Complexity**: Is the complexity assessment realistic based on similar tickets?

Provide detailed technical feedback including:
- Specific improvement recommendations
- Technical risks and mitigation strategies  
- Architecture and implementation considerations
- Resource and timeline implications

Format your response as JSON:
{
    "summary_clarity": 0.85,
    "user_story_format": 0.90,
    "acceptance_criteria": 0.80,
    "technical_feasibility": 0.95,
    "business_value": 0.85,
    "architectural_alignment": 0.90,
    "implementation_complexity": 0.85,
    "overall_score": 0.87,
    "approved": true,
    "feedback": "Comprehensive technical feedback with specific recommendations",
    "recommendations": ["Specific improvement 1", "Technical consideration 2", "Risk mitigation 3"],
    "technical_risks": ["Risk 1", "Risk 2"],
    "resource_estimates": "Implementation timeline and resource requirements"
}'''
        }
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in config[key]:
                                config[key][subkey] = subvalue
                return config
        else:
            # Create default config file
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            return default_config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return default_config

def save_user_config(config_data):
    """Save user configuration to config.yaml"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        logger.info("Configuration saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

@app.route('/')
def index():
    """Main ticket creation page"""
    config = load_user_config()
    return render_template('index.html', user_config=config)

@app.route('/config')
def config_page():
    """Configuration management page"""
    config = load_user_config()
    return render_template('config.html', current_config=config)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '0.1.0',
        'orchestrator_available': create_jira_ticket_with_ai is not None
    })

@app.route('/api/create-ticket', methods=['POST'])
def create_ticket():
    """Create ticket endpoint"""
    try:
        data = request.get_json()
        if not data or 'user_request' not in data:
            return jsonify({'error': 'Missing user_request in request body'}), 400
            
        user_request = data['user_request'].strip()
        if not user_request:
            return jsonify({'error': 'User request cannot be empty'}), 400
            
        # Generate unique workflow ID
        workflow_id = f"workflow_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        # Store workflow info
        active_workflows[workflow_id] = {
            'status': 'started',
            'created_at': datetime.now().isoformat(),
            'user_request': user_request,
            'context': data.get('context', {})
        }
        
        logger.info(f"Starting workflow {workflow_id} for request: {user_request[:100]}...")
        
        # Start workflow in background thread
        thread = threading.Thread(
            target=execute_workflow_with_updates,
            args=(workflow_id, user_request, data.get('context', {}))
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'workflow_id': workflow_id, 'status': 'started'})
        
    except Exception as e:
        logger.error(f"Error in create_ticket: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-config', methods=['POST'])
def save_config():
    """Save user configuration"""
    try:
        config_data = request.get_json()
        if not config_data:
            return jsonify({'error': 'No configuration data provided'}), 400
            
        if save_user_config(config_data):
            return jsonify({'success': True, 'message': 'Configuration saved successfully'})
        else:
            return jsonify({'error': 'Failed to save configuration'}), 500
            
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/prompts')
def prompts_page():
    """Prompts management page"""
    config = load_user_config()
    return render_template('prompts.html', current_config=config)

@app.route('/api/save-prompts', methods=['POST'])
def save_prompts():
    """Save agent prompts"""
    try:
        data = request.get_json()
        if not data or 'agent_prompts' not in data:
            return jsonify({'error': 'No agent prompts data provided'}), 400
        
        # Load current config
        config = load_user_config()
        
        # Update agent prompts
        config['agent_prompts'] = data['agent_prompts']
        
        # Save updated config
        if save_user_config(config):
            return jsonify({'success': True, 'message': 'Agent prompts saved successfully'})
        else:
            return jsonify({'error': 'Failed to save agent prompts'}), 500
            
    except Exception as e:
        logger.error(f"Error saving prompts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset-prompts', methods=['POST'])
def reset_prompts():
    """Reset agent prompts to default values"""
    try:
        # Load current config
        config = load_user_config()
        
        # Get default prompts from the default_config in load_user_config function
        default_config = {
            'agent_prompts': {
                'pm_agent_basic': '''You are an expert Product Manager creating JIRA tickets. 

User Request: {user_request}

Additional Context from GitBook: {gitbook_context}

Create a comprehensive JIRA ticket with:
1. Clear, actionable summary (max 100 characters)
2. Detailed description with business context
3. Specific acceptance criteria (3-5 bullet points)
4. Technical considerations
5. Definition of Done

Format your response as JSON:
{
  "summary": "Brief ticket title",
  "description": "Detailed description with context",
  "acceptance_criteria": ["Criterion 1", "Criterion 2", "Criterion 3"],
  "technical_notes": "Any technical considerations",
  "definition_of_done": "Clear completion criteria"
}''',
                'pm_agent_enhanced': '''You are an expert Product Manager with access to company documentation and historical JIRA tickets. 

**User Request:** "{user_request}"
{context_summary}
{gitbook_context}
{similar_tickets_context}

**TASK:** Create a professional JIRA ticket that leverages the research context above. Reference specific documentation or similar ticket patterns where relevant to show you've incorporated the research.

Following Atlassian best practices and the company patterns from documentation/similar tickets, create a professional ticket with these components:

**SUMMARY REQUIREMENTS:**
- Start with an action verb (Implement, Fix, Create, Update, etc.)
- Be specific and descriptive (50-200 characters)
- Follow format: "[Verb] [what] [for whom/why]"

**DESCRIPTION STRUCTURE:**
1. **Story/Background**: Why this work matters and who benefits
2. **Business Value**: Clear impact on business metrics/goals
3. **Context**: Reference documentation and similar implementations found

**ACCEPTANCE CRITERIA:**
- Use specific, testable, measurable criteria
- Format as numbered list (3-6 criteria maximum)
- Each criterion should clearly define "done"

**TECHNICAL APPROACH:**
- Reference company standards and documentation patterns
- Include implementation considerations
- Note any architectural decisions

Use professional product management language and leverage insights from the provided context.

IMPORTANT: Format response as clean JSON (no markdown blocks):
{
    "summary": "Action verb + clear description of what will be implemented",
    "description": "Comprehensive story explaining why this work matters, who benefits, and business context based on research",
    "acceptance_criteria": ["Specific testable criterion 1", "Specific testable criterion 2", "Specific testable criterion 3"],
    "business_value": "Quantifiable business impact with metrics and strategic alignment based on company goals",
    "technical_considerations": "Implementation approach referencing company standards, architecture, and documentation patterns",
    "estimated_complexity": "Low/Medium/High based on technical scope and dependencies",
    "dependencies": ["Dependency 1 based on similar tickets", "Dependency 2 if applicable"],
    "risk_assessment": "Key risks and mitigation strategies based on historical patterns and technical complexity"
}''',
                'tech_lead_basic': '''You are a Senior Tech Lead reviewing a JIRA ticket for quality and completeness.

Ticket Draft:
Summary: {ticket_draft.get('summary', '')}
Description: {ticket_draft.get('description', '')}
Acceptance Criteria: {ticket_draft.get('acceptance_criteria', [])}

Rate this ticket on 5 dimensions (0.0 to 1.0 each):
1. Summary Clarity: Is the summary clear and actionable?
2. User Story Format: Does it follow proper user story structure?
3. Acceptance Criteria: Are they specific, measurable, and testable?
4. Technical Feasibility: Is the request technically sound?
5. Business Value: Is the business value clear?

Also provide:
- Overall quality score (average of 5 dimensions)
- Specific feedback for improvements
- Technical considerations and risks
- Approval recommendation (approve/needs_improvement)

Format as JSON:
{
  "scores": {
    "summary_clarity": 0.8,
    "user_story_format": 0.7,
    "acceptance_criteria": 0.9,
    "technical_feasibility": 0.8,
    "business_value": 0.7
  },
  "overall_score": 0.78,
  "feedback": "Specific improvement suggestions",
  "technical_notes": "Technical considerations",
  "recommendation": "approve" or "needs_improvement",
  "risks": ["Risk 1", "Risk 2"]
}''',
                'tech_lead_enhanced': '''You are a Senior Tech Lead and Software Architect with deep knowledge of company systems and implementation patterns.

Review this JIRA ticket for quality, technical feasibility, and alignment with company standards:

**Ticket to Review:**
Summary: {ticket_draft.get('summary', 'N/A')}
Description: {ticket_draft.get('description', 'N/A')}
Acceptance Criteria: {ticket_draft.get('acceptance_criteria', [])}
Business Value: {ticket_draft.get('business_value', 'N/A')}
Technical Considerations: {ticket_draft.get('technical_considerations', 'N/A')}
Estimated Complexity: {ticket_draft.get('estimated_complexity', 'N/A')}
{technical_context}
{complexity_context}

Based on the technical documentation and implementation patterns from similar tickets, evaluate this ticket on these dimensions (score 0.0-1.0 each):

1. **Summary Clarity**: Is the title clear, specific, and actionable?
2. **User Story Format**: Does it follow proper user story structure and company conventions?
3. **Acceptance Criteria**: Are criteria specific, measurable, testable, and complete?
4. **Technical Feasibility**: Is this technically achievable with current architecture and constraints?
5. **Business Value**: Is the business impact clearly articulated and measurable?
6. **Architectural Alignment**: Does this align with company technical standards and patterns?
7. **Implementation Complexity**: Is the complexity assessment realistic based on similar tickets?

Provide detailed technical feedback including:
- Specific improvement recommendations
- Technical risks and mitigation strategies  
- Architecture and implementation considerations
- Resource and timeline implications

Format your response as JSON:
{
    "summary_clarity": 0.85,
    "user_story_format": 0.90,
    "acceptance_criteria": 0.80,
    "technical_feasibility": 0.95,
    "business_value": 0.85,
    "architectural_alignment": 0.90,
    "implementation_complexity": 0.85,
    "overall_score": 0.87,
    "approved": true,
    "feedback": "Comprehensive technical feedback with specific recommendations",
    "recommendations": ["Specific improvement 1", "Technical consideration 2", "Risk mitigation 3"],
    "technical_risks": ["Risk 1", "Risk 2"],
    "resource_estimates": "Implementation timeline and resource requirements"
}'''
            }
        }
        
        # Update with default prompts
        config['agent_prompts'] = default_config['agent_prompts']
        
        # Save updated config
        if save_user_config(config):
            return jsonify({'success': True, 'message': 'Agent prompts reset to default values'})
        else:
            return jsonify({'error': 'Failed to reset agent prompts'}), 500
            
    except Exception as e:
        logger.error(f"Error resetting prompts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflow/<workflow_id>')
def get_workflow_status(workflow_id):
    """Get workflow status"""
    if workflow_id in active_workflows:
        return jsonify(active_workflows[workflow_id])
    else:
        return jsonify({'error': 'Workflow not found'}), 404

def execute_workflow_with_updates(workflow_id, user_request, context):
    """Execute workflow with real-time updates via WebSocket"""
    def progress_callback(update):
        """Callback function to send progress updates"""
        try:
            # Update active workflows
            if workflow_id in active_workflows:
                active_workflows[workflow_id].update(update)
            
            # Emit to all connected clients (in a real multi-user system, this would be user-specific)
            socketio.emit('workflow_update', {
                'workflow_id': workflow_id,
                **update
            })
            
            logger.info(f"Progress update for {workflow_id}: {update.get('message', 'No message')}")
            
        except Exception as e:
            logger.error(f"Error in progress callback: {e}")
    
    try:
        # Emit start event
        socketio.emit('workflow_start', {
            'workflow_id': workflow_id,
            'status': 'started',
            'message': 'Initializing AI agents...'
        })
        
        if create_jira_ticket_with_ai is None:
            # Mock workflow for testing when orchestrator is not available
            logger.warning("Orchestrator not available, running mock workflow")
            
            # Simulate workflow steps
            steps = [
                {'agent': 'PM Agent', 'progress': 20, 'message': 'Analyzing your request...'},
                {'agent': 'PM Agent', 'progress': 40, 'message': 'Researching context and similar tickets...'},
                {'agent': 'Business Rules', 'progress': 50, 'message': 'Applying business rules...'},
                {'agent': 'Tech Lead Agent', 'progress': 70, 'message': 'Reviewing technical feasibility...'},
                {'agent': 'Tech Lead Agent', 'progress': 85, 'message': 'Quality score: 0.92 - Excellent!'},
                {'agent': 'Jira Creator', 'progress': 95, 'message': 'Creating ticket in JIRA...'},
                {'agent': 'System', 'progress': 100, 'message': 'Workflow completed successfully'}
            ]
            
            for step in steps:
                time.sleep(2)  # Simulate processing time
                progress_callback(step)
            
            # Mock result
            result = {
                'success': True,
                'ticket_key': 'DEMO-1234',
                'ticket_url': 'https://demo.atlassian.net/browse/DEMO-1234',
                'quality_metrics': {'final_quality_score': 0.92},
                'total_execution_time': 8.0
            }
        else:
            # Execute real workflow
            logger.info(f"Executing real workflow for {workflow_id}")
            result = create_jira_ticket_with_ai(
                user_request=user_request,
                context=context,
                progress_callback=progress_callback
            )
        
        # Update workflow status
        active_workflows[workflow_id].update({
            'status': 'completed',
            'result': result,
            'completed_at': datetime.now().isoformat()
        })
        
        # Emit completion
        socketio.emit('workflow_complete', {
            'workflow_id': workflow_id,
            'result': result
        })
        
        logger.info(f"Workflow {workflow_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in workflow execution: {e}")
        
        # Update workflow status
        active_workflows[workflow_id].update({
            'status': 'failed',
            'error': str(e),
            'completed_at': datetime.now().isoformat()
        })
        
        # Emit error
        socketio.emit('workflow_error', {
            'workflow_id': workflow_id,
            'error': str(e)
        })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'message': 'Connected to PM Jira Agent'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

# Serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    # Ensure config directory exists
    os.makedirs('config', exist_ok=True)
    
    # Run the application
    logger.info("Starting PM Jira Agent Phase 0 Web Interface")
    logger.info(f"Configuration directory: {os.path.abspath('config')}")
    
    # Check if we're in development mode
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=int(os.environ.get('PORT', 5000)),
        debug=debug_mode,
        allow_unsafe_werkzeug=True
    )