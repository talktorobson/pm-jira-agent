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
            'name': 'Product Manager',
            'email': 'pm@company.com',
            'team': 'Product Team'
        },
        'jira': {
            'base_url': 'https://yourcompany.atlassian.net',
            'project_key': 'PROJ',
            'default_issue_type': 'Story',
            'default_priority': 'Medium'
        },
        'gitbook': {
            'space_id': '',
            'enabled': False
        },
        'custom_prompts': {
            'company_context': 'We are a technology company focused on innovative solutions',
            'writing_style': 'professional',
            'stakeholder_mapping': {
                'Security Team': 'security@company.com',
                'UX Team': 'ux@company.com',
                'Engineering': 'dev@company.com'
            }
        },
        'business_rules': {
            'ui_ux_guidelines': 'Follow modern UI/UX best practices',
            'security_requirements': 'All user data must be secure',
            'performance_standards': 'Optimize for fast user experience'
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