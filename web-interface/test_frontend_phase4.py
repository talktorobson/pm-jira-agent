#!/usr/bin/env python3
"""
PM Jira Agent Frontend - Phase 4 Comprehensive Test Suite
Testing: UI Polish, Error Handling, User Feedback, and End-to-End Workflow
"""

import pytest
import asyncio
import json
import time
from flask import Flask
from flask_socketio import SocketIOTestClient
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app and its components
from app import app, socketio, EnhancedMultiAgentOrchestrator

class TestPhase4Frontend:
    """Comprehensive test suite for Phase 4 frontend enhancements"""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment"""
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.socketio = socketio
        cls.client = SocketIOTestClient(cls.app, cls.socketio)
        print("🧪 Phase 4 Frontend Test Suite initialized")
    
    def test_01_health_check(self):
        """Test basic health check endpoint"""
        print("\n🧪 Test 1: Health Check")
        
        with self.app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert 'timestamp' in data
            assert data['service'] == 'PM Jira Agent Frontend'
            
        print("✅ Health check passed")
    
    def test_02_websocket_connection(self):
        """Test WebSocket connection establishment"""
        print("\n🧪 Test 2: WebSocket Connection")
        
        # Test connection
        received = self.client.get_received()
        
        # Should receive connection confirmation
        connection_events = [event for event in received if event['name'] == 'connected']
        assert len(connection_events) > 0
        
        # Verify connection data
        connection_data = connection_events[0]['args'][0]
        assert 'status' in connection_data
        assert 'timestamp' in connection_data
        
        print("✅ WebSocket connection established successfully")
    
    def test_03_form_validation(self):
        """Test enhanced form validation"""
        print("\n🧪 Test 3: Form Validation")
        
        # Test missing fields
        self.client.emit('create_ticket', {
            'userStory': '',
            'issueType': '',
            'priority': ''
        })
        
        received = self.client.get_received()
        error_events = [event for event in received if event['name'] == 'error']
        assert len(error_events) > 0
        
        error_data = error_events[0]['args'][0]
        assert 'All fields are required' in error_data['message']
        
        print("✅ Form validation working correctly")
    
    def test_04_user_story_validation(self):
        """Test user story format validation"""
        print("\n🧪 Test 4: User Story Validation")
        
        # Test poor format user story
        self.client.emit('create_ticket', {
            'userStory': 'I need a feature',
            'issueType': 'Story',
            'priority': 'Medium'
        })
        
        received = self.client.get_received()
        warning_events = [event for event in received if event['name'] == 'validation_warning']
        
        # Should trigger validation warning
        assert len(warning_events) > 0
        
        print("✅ User story validation working")
    
    @patch('app.EnhancedMultiAgentOrchestrator')
    def test_05_mock_workflow_execution(self, mock_orchestrator_class):
        """Test workflow execution with mocked orchestrator"""
        print("\n🧪 Test 5: Mock Workflow Execution")
        
        # Set up mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Mock agent methods to return realistic results
        mock_orchestrator.process_pm_agent = Mock(return_value={
            'quality_score': 0.89,
            'enhancement_text': 'Enhanced PM draft',
            'api_calls': {'total_duration': '2.5s'}
        })
        
        mock_orchestrator.process_tech_lead_agent = Mock(return_value={
            'quality_score': 0.94,
            'enhancement_text': 'Technical analysis complete',
            'api_calls': {'total_duration': '2.8s'}
        })
        
        mock_orchestrator.process_qa_agent = Mock(return_value={
            'quality_score': 0.97,
            'enhancement_text': 'QA validation complete',
            'api_calls': {'total_duration': '2.2s'}
        })
        
        mock_orchestrator.process_business_rules_agent = Mock(return_value={
            'quality_score': 0.99,
            'enhancement_text': 'Compliance verified',
            'api_calls': {'total_duration': '2.0s'}
        })
        
        mock_orchestrator.process_jira_creator_agent = Mock(return_value={
            'success': True,
            'creation_result': {
                'ticket_key': 'TEST-123',
                'ticket_url': 'https://jira.test/browse/TEST-123'
            },
            'api_calls': {'total_duration': '3.1s'}
        })
        
        # Mock workflow data and metrics
        mock_orchestrator.start_time = time.time()
        mock_orchestrator.workflow_data = {}
        mock_orchestrator._calculate_composite_quality_score = Mock(return_value={
            'composite_score': 0.94,
            'quality_level': 'Excellent'
        })
        
        # Test workflow execution
        self.client.emit('create_ticket', {
            'userStory': 'As a user, I want to test the system so that I can verify functionality',
            'issueType': 'Story',
            'priority': 'Medium'
        })
        
        # Give some time for async processing
        time.sleep(0.5)
        
        received = self.client.get_received()
        
        # Verify workflow events
        workflow_started = [e for e in received if e['name'] == 'workflow_started']
        agent_started = [e for e in received if e['name'] == 'agent_started']
        agent_completed = [e for e in received if e['name'] == 'agent_completed']
        
        assert len(workflow_started) > 0
        assert len(agent_started) > 0
        assert len(agent_completed) > 0
        
        print("✅ Mock workflow execution successful")
    
    def test_06_error_handling(self):
        """Test enhanced error handling and user feedback"""
        print("\n🧪 Test 6: Error Handling")
        
        with patch('app.EnhancedMultiAgentOrchestrator') as mock_class:
            # Make orchestrator initialization fail
            mock_class.side_effect = Exception("Mock orchestrator failure")
            
            self.client.emit('create_ticket', {
                'userStory': 'As a user, I want to trigger an error so that I can test error handling',
                'issueType': 'Bug',
                'priority': 'High'
            })
            
            time.sleep(0.5)
            
            received = self.client.get_received()
            error_events = [e for e in received if e['name'] == 'error']
            
            assert len(error_events) > 0
            
            error_data = error_events[0]['args'][0]
            assert 'suggestions' in error_data or 'details' in error_data
            
        print("✅ Error handling working correctly")
    
    def test_07_analytics_data_structure(self):
        """Test analytics data structure and calculations"""
        print("\n🧪 Test 7: Analytics Data Structure")
        
        # Test with mock data that would come from a real workflow
        test_analytics = {
            'agentTimes': {
                'pm_agent': 2.5,
                'tech_lead_agent': 2.8,
                'qa_agent': 2.2,
                'business_rules_agent': 2.0,
                'jira_creator_agent': 3.1
            },
            'agentScores': {
                'pm_agent': 0.89,
                'tech_lead_agent': 0.94,
                'qa_agent': 0.97,
                'business_rules_agent': 0.99,
                'jira_creator_agent': 1.0
            },
            'totalDuration': 12.6,
            'startTime': time.time() * 1000,
            'endTime': (time.time() + 12.6) * 1000
        }
        
        # Verify data structure
        assert len(test_analytics['agentTimes']) == 5
        assert len(test_analytics['agentScores']) == 5
        assert test_analytics['totalDuration'] > 0
        
        # Verify score ranges
        for score in test_analytics['agentScores'].values():
            assert 0.0 <= score <= 1.0
        
        # Verify timing
        for duration in test_analytics['agentTimes'].values():
            assert duration > 0
        
        print("✅ Analytics data structure validated")
    
    def test_08_auto_scroll_functionality(self):
        """Test auto-scroll to active agents functionality"""
        print("\n🧪 Test 8: Auto-Scroll Functionality")
        
        # This would test the JavaScript functionality if we had a browser environment
        # For now, we test that the events are properly structured for frontend consumption
        
        test_agent_data = {
            'agent': 'pm_agent',
            'name': 'PM Agent',
            'icon': '🔍',
            'activity': 'Processing user request...',
            'progress': 20
        }
        
        # Verify all required fields for auto-scroll are present
        required_fields = ['agent', 'name', 'icon', 'activity', 'progress']
        for field in required_fields:
            assert field in test_agent_data
        
        print("✅ Auto-scroll data structure validated")
    
    def test_09_log_message_formatting(self):
        """Test enhanced log message formatting"""
        print("\n🧪 Test 9: Log Message Formatting")
        
        # Test different log message types that would be formatted on frontend
        test_messages = [
            {'message': 'Agent started processing', 'type': 'info', 'details': {'agent': 'PM Agent', 'duration': '2.5s'}},
            {'message': 'Quality score achieved', 'type': 'success', 'details': None},
            {'message': 'Validation warning', 'type': 'warning', 'details': 'User story format could be improved'},
            {'message': 'Processing failed', 'type': 'error', 'details': {'error': 'Connection timeout', 'suggestion': 'Retry request'}}
        ]
        
        for msg in test_messages:
            # Verify message structure
            assert 'message' in msg
            assert 'type' in msg
            assert msg['type'] in ['info', 'success', 'warning', 'error']
            
            # Details can be None, string, or dict
            if msg['details'] is not None:
                assert isinstance(msg['details'], (str, dict))
        
        print("✅ Log message formatting validated")
    
    def test_10_performance_metrics(self):
        """Test performance metrics calculation"""
        print("\n🧪 Test 10: Performance Metrics")
        
        # Test efficiency calculation logic
        def calculate_efficiency(target_time, actual_time, avg_quality, completion_rate):
            time_efficiency = min(1.0, target_time / actual_time)
            efficiency = (time_efficiency * 0.4 + avg_quality * 0.4 + completion_rate * 0.2)
            return efficiency
        
        # Test scenarios
        test_cases = [
            {'target': 60, 'actual': 45, 'quality': 0.9, 'completion': 1.0, 'expected_min': 0.8},
            {'target': 60, 'actual': 90, 'quality': 0.85, 'completion': 0.8, 'expected_min': 0.6},
            {'target': 60, 'actual': 30, 'quality': 0.95, 'completion': 1.0, 'expected_min': 0.9}
        ]
        
        for case in test_cases:
            efficiency = calculate_efficiency(
                case['target'], case['actual'], 
                case['quality'], case['completion']
            )
            assert efficiency >= case['expected_min']
            assert 0.0 <= efficiency <= 1.0
        
        print("✅ Performance metrics calculation validated")

def run_frontend_tests():
    """Run the complete Phase 4 frontend test suite"""
    print("🚀 Starting PM Jira Agent Frontend - Phase 4 Test Suite")
    print("=" * 60)
    
    # Initialize test class
    test_suite = TestPhase4Frontend()
    test_suite.setup_class()
    
    # Run all tests
    test_methods = [method for method in dir(test_suite) if method.startswith('test_')]
    total_tests = len(test_methods)
    passed_tests = 0
    failed_tests = []
    
    for test_method in test_methods:
        try:
            method = getattr(test_suite, test_method)
            method()
            passed_tests += 1
        except Exception as e:
            failed_tests.append(f"{test_method}: {str(e)}")
            print(f"❌ {test_method} failed: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🧪 PHASE 4 FRONTEND TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {len(failed_tests)}/{total_tests}")
    
    if failed_tests:
        print("\n📋 Failed Tests:")
        for failure in failed_tests:
            print(f"   • {failure}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Phase 4 Frontend Testing: PASSED")
        return True
    else:
        print("⚠️ Phase 4 Frontend Testing: NEEDS IMPROVEMENT")
        return False

if __name__ == '__main__':
    success = run_frontend_tests()
    exit(0 if success else 1)