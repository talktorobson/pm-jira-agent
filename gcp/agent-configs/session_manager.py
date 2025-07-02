#!/usr/bin/env python3

"""
Vertex AI Agent Engine Session Manager
Advanced session management with user context and streaming responses
Based on latest ADK documentation and best practices
"""

import os
import time
import json
import logging
import uuid
from typing import Dict, Any, List, Optional, Iterator, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import vertexai
from vertexai.preview import agent_engines

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SessionInfo:
    """Session information and metadata"""
    session_id: str
    user_id: str
    agent_resource_name: str
    agent_display_name: str
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    total_tokens: int = 0
    context: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["last_activity"] = self.last_activity.isoformat()
        return data

@dataclass
class StreamingEvent:
    """Streaming response event"""
    event_type: str  # 'thinking', 'tool_use', 'response', 'complete'
    content: str
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class SessionManager:
    """Advanced session manager for Vertex AI Agent Engine"""
    
    def __init__(self, project_id: str = "service-execution-uat-bb7", location: str = "europe-west9"):
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Session storage (in production, would use Cloud Firestore or similar)
        self.sessions: Dict[str, SessionInfo] = {}
        self.session_timeout_hours = 24  # Sessions expire after 24 hours
        
        # Agent registry
        self.agent_registry: Dict[str, Any] = {}
        
        logger.info(f"Session Manager initialized for project {project_id}")
    
    def register_agent(self, resource_name: str, display_name: str, agent_type: str) -> bool:
        """Register an agent for session management"""
        
        try:
            # Get agent instance to verify it exists
            agent = agent_engines.get(resource_name)
            
            self.agent_registry[agent_type] = {
                "resource_name": resource_name,
                "display_name": display_name,
                "agent_instance": agent,
                "registered_at": datetime.now()
            }
            
            logger.info(f"✅ Registered agent {agent_type}: {display_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register agent {agent_type}: {str(e)}")
            return False
    
    def create_session(self, user_id: str, agent_type: str, context: Optional[Dict[str, Any]] = None) -> Optional[SessionInfo]:
        """Create a new session for a user with a specific agent"""
        
        try:
            # Check if agent is registered
            if agent_type not in self.agent_registry:
                logger.error(f"Agent type {agent_type} not registered")
                return None
            
            agent_info = self.agent_registry[agent_type]
            
            # Generate session ID
            session_id = f"{agent_type}_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Create session info
            session_info = SessionInfo(
                session_id=session_id,
                user_id=user_id,
                agent_resource_name=agent_info["resource_name"],
                agent_display_name=agent_info["display_name"],
                created_at=datetime.now(),
                last_activity=datetime.now(),
                context=context or {}
            )
            
            # Store session
            self.sessions[session_id] = session_info
            
            logger.info(f"✅ Created session {session_id} for user {user_id} with {agent_type}")
            return session_info
            
        except Exception as e:
            logger.error(f"❌ Failed to create session: {str(e)}")
            return None
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        
        session = self.sessions.get(session_id)
        
        if session is None:
            logger.warning(f"Session {session_id} not found")
            return None
        
        # Check if session has expired
        if self._is_session_expired(session):
            logger.info(f"Session {session_id} has expired, removing")
            del self.sessions[session_id]
            return None
        
        return session
    
    def list_user_sessions(self, user_id: str) -> List[SessionInfo]:
        """List all active sessions for a user"""
        
        user_sessions = []
        
        for session in self.sessions.values():
            if session.user_id == user_id and not self._is_session_expired(session):
                user_sessions.append(session)
        
        return user_sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a specific session"""
        
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"✅ Deleted session {session_id}")
            return True
        else:
            logger.warning(f"Session {session_id} not found for deletion")
            return False
    
    def query_with_session(self, session_id: str, message: str, 
                          context_update: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query agent with session context"""
        
        session = self.get_session(session_id)
        if session is None:
            return {
                "success": False,
                "error": "Session not found or expired",
                "session_id": session_id
            }
        
        try:
            # Get agent instance
            agent_info = None
            for agent_type, info in self.agent_registry.items():
                if info["resource_name"] == session.agent_resource_name:
                    agent_info = info
                    break
            
            if agent_info is None:
                return {
                    "success": False,
                    "error": "Agent not found in registry",
                    "session_id": session_id
                }
            
            agent = agent_info["agent_instance"]
            
            # Update context if provided
            if context_update:
                session.context.update(context_update)
            
            # Prepare contextualized message
            contextualized_message = self._prepare_contextualized_message(message, session)
            
            # Query agent
            start_time = time.time()
            response = agent.query(input=contextualized_message)
            execution_time = time.time() - start_time
            
            # Update session
            session.last_activity = datetime.now()
            session.message_count += 1
            
            logger.info(f"✅ Query completed for session {session_id} in {execution_time:.2f}s")
            
            return {
                "success": True,
                "response": str(response),
                "session_id": session_id,
                "execution_time": execution_time,
                "message_count": session.message_count,
                "agent_name": session.agent_display_name
            }
            
        except Exception as e:
            logger.error(f"❌ Query failed for session {session_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    def stream_query_with_session(self, session_id: str, message: str, 
                                 context_update: Optional[Dict[str, Any]] = None) -> Iterator[StreamingEvent]:
        """Stream query response with session context"""
        
        session = self.get_session(session_id)
        if session is None:
            yield StreamingEvent(
                event_type="error",
                content=f"Session {session_id} not found or expired"
            )
            return
        
        try:
            # Get agent instance
            agent_info = None
            for agent_type, info in self.agent_registry.items():
                if info["resource_name"] == session.agent_resource_name:
                    agent_info = info
                    break
            
            if agent_info is None:
                yield StreamingEvent(
                    event_type="error",
                    content="Agent not found in registry"
                )
                return
            
            agent = agent_info["agent_instance"]
            
            # Update context if provided
            if context_update:
                session.context.update(context_update)
            
            # Prepare contextualized message
            contextualized_message = self._prepare_contextualized_message(message, session)
            
            # Start streaming
            yield StreamingEvent(
                event_type="thinking",
                content="Processing your request...",
                metadata={"session_id": session_id, "agent": session.agent_display_name}
            )
            
            # Stream query (in real implementation, would use actual streaming)
            # For now, simulate streaming with chunks
            try:
                response = agent.query(input=contextualized_message)
                response_text = str(response)
                
                # Simulate streaming by chunking response
                chunk_size = 50
                for i in range(0, len(response_text), chunk_size):
                    chunk = response_text[i:i + chunk_size]
                    yield StreamingEvent(
                        event_type="response",
                        content=chunk,
                        metadata={"chunk_index": i // chunk_size}
                    )
                    time.sleep(0.1)  # Simulate network delay
                
                # Update session
                session.last_activity = datetime.now()
                session.message_count += 1
                
                yield StreamingEvent(
                    event_type="complete",
                    content="Response complete",
                    metadata={
                        "session_id": session_id,
                        "message_count": session.message_count,
                        "total_response_length": len(response_text)
                    }
                )
                
            except Exception as e:
                yield StreamingEvent(
                    event_type="error",
                    content=f"Query execution failed: {str(e)}"
                )
            
        except Exception as e:
            yield StreamingEvent(
                event_type="error",
                content=f"Stream setup failed: {str(e)}"
            )
    
    def get_session_history(self, session_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get session conversation history"""
        
        session = self.get_session(session_id)
        if session is None:
            return {
                "success": False,
                "error": "Session not found or expired"
            }
        
        # In a real implementation, would retrieve actual conversation history
        # For now, return session metadata and summary
        return {
            "success": True,
            "session_info": session.to_dict(),
            "history_summary": {
                "total_messages": session.message_count,
                "session_duration_minutes": int((session.last_activity - session.created_at).total_seconds() / 60),
                "avg_tokens_per_message": session.total_tokens / max(session.message_count, 1)
            },
            "context": session.context
        }
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Get analytics for all sessions"""
        
        active_sessions = [s for s in self.sessions.values() if not self._is_session_expired(s)]
        
        # Calculate analytics
        total_sessions = len(active_sessions)
        total_messages = sum(s.message_count for s in active_sessions)
        total_users = len(set(s.user_id for s in active_sessions))
        
        # Agent usage
        agent_usage = {}
        for session in active_sessions:
            agent_name = session.agent_display_name
            if agent_name not in agent_usage:
                agent_usage[agent_name] = {"sessions": 0, "messages": 0}
            agent_usage[agent_name]["sessions"] += 1
            agent_usage[agent_name]["messages"] += session.message_count
        
        # Session duration analysis
        durations = []
        for session in active_sessions:
            duration_minutes = (session.last_activity - session.created_at).total_seconds() / 60
            durations.append(duration_minutes)
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_sessions": total_sessions,
            "total_users": total_users,
            "total_messages": total_messages,
            "avg_messages_per_session": total_messages / max(total_sessions, 1),
            "avg_session_duration_minutes": round(avg_duration, 2),
            "agent_usage": agent_usage,
            "registered_agents": len(self.agent_registry)
        }
    
    def _is_session_expired(self, session: SessionInfo) -> bool:
        """Check if session has expired"""
        
        expiry_time = session.last_activity + timedelta(hours=self.session_timeout_hours)
        return datetime.now() > expiry_time
    
    def _prepare_contextualized_message(self, message: str, session: SessionInfo) -> str:
        """Prepare message with session context"""
        
        context_info = []
        
        # Add session context
        if session.context:
            context_info.append(f"Session Context: {json.dumps(session.context, indent=2)}")
        
        # Add conversation context
        if session.message_count > 0:
            context_info.append(f"This is message #{session.message_count + 1} in our conversation.")
        
        # Add user context
        context_info.append(f"User ID: {session.user_id}")
        
        if context_info:
            context_section = "\n".join(context_info)
            return f"CONTEXT:\n{context_section}\n\nUSER MESSAGE:\n{message}"
        else:
            return message

class MultiAgentSessionWorkflow:
    """Multi-agent workflow with session management"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.workflow_sessions = {}  # workflow_id -> list of session_ids
    
    def start_workflow(self, user_id: str, user_request: str, 
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a multi-agent workflow with session management"""
        
        workflow_id = f"workflow_{user_id}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Create sessions for each agent
            pm_session = self.session_manager.create_session(
                user_id, "pm_agent", 
                {**context, "workflow_id": workflow_id, "phase": "analysis"} if context else {"workflow_id": workflow_id, "phase": "analysis"}
            )
            
            tech_lead_session = self.session_manager.create_session(
                user_id, "tech_lead_agent",
                {**context, "workflow_id": workflow_id, "phase": "review"} if context else {"workflow_id": workflow_id, "phase": "review"}
            )
            
            jira_creator_session = self.session_manager.create_session(
                user_id, "jira_creator_agent",
                {**context, "workflow_id": workflow_id, "phase": "creation"} if context else {"workflow_id": workflow_id, "phase": "creation"}
            )
            
            if not all([pm_session, tech_lead_session, jira_creator_session]):
                return {
                    "success": False,
                    "error": "Failed to create all required sessions",
                    "workflow_id": workflow_id
                }
            
            # Store workflow session mapping
            self.workflow_sessions[workflow_id] = {
                "pm_session_id": pm_session.session_id,
                "tech_lead_session_id": tech_lead_session.session_id,
                "jira_creator_session_id": jira_creator_session.session_id,
                "user_id": user_id,
                "created_at": datetime.now(),
                "status": "active"
            }
            
            logger.info(f"✅ Started workflow {workflow_id} with 3 agent sessions")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "sessions": {
                    "pm_session_id": pm_session.session_id,
                    "tech_lead_session_id": tech_lead_session.session_id,
                    "jira_creator_session_id": jira_creator_session.session_id
                },
                "next_step": "pm_analysis"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start workflow: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    def execute_workflow_step(self, workflow_id: str, step: str, 
                            message: str, context_update: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific step in the workflow"""
        
        if workflow_id not in self.workflow_sessions:
            return {
                "success": False,
                "error": "Workflow not found"
            }
        
        workflow_info = self.workflow_sessions[workflow_id]
        
        # Map steps to session IDs
        step_session_mapping = {
            "pm_analysis": workflow_info["pm_session_id"],
            "tech_lead_review": workflow_info["tech_lead_session_id"],
            "jira_creation": workflow_info["jira_creator_session_id"]
        }
        
        if step not in step_session_mapping:
            return {
                "success": False,
                "error": f"Invalid workflow step: {step}"
            }
        
        session_id = step_session_mapping[step]
        
        # Execute query with session
        result = self.session_manager.query_with_session(
            session_id, message, context_update
        )
        
        # Add workflow context to result
        result["workflow_id"] = workflow_id
        result["workflow_step"] = step
        
        return result

def main():
    """Main function for testing session management"""
    
    print("🔗 Vertex AI Agent Engine Session Manager")
    print("=" * 50)
    
    # Initialize session manager
    session_manager = SessionManager()
    
    # Register sample agents (would use real resource names in production)
    sample_agents = [
        ("projects/123/locations/europe-west9/agents/pm-agent", "PM Agent", "pm_agent"),
        ("projects/123/locations/europe-west9/agents/tech-lead-agent", "Tech Lead Agent", "tech_lead_agent"),
        ("projects/123/locations/europe-west9/agents/jira-creator-agent", "Jira Creator Agent", "jira_creator_agent")
    ]
    
    print("\n📝 Registering sample agents...")
    for resource_name, display_name, agent_type in sample_agents:
        # In real implementation, would register actual agents
        session_manager.agent_registry[agent_type] = {
            "resource_name": resource_name,
            "display_name": display_name,
            "agent_instance": None,  # Would be actual agent instance
            "registered_at": datetime.now()
        }
        print(f"  ✅ Registered {agent_type}: {display_name}")
    
    # Test session creation
    print("\n🆕 Creating test sessions...")
    test_user = "user_001"
    
    pm_session = session_manager.create_session(
        test_user, "pm_agent", 
        {"project": "AHSSI", "priority": "High"}
    )
    
    if pm_session:
        print(f"  ✅ Created PM session: {pm_session.session_id}")
    
    # Test multi-agent workflow
    print("\n🔄 Testing multi-agent workflow...")
    workflow_manager = MultiAgentSessionWorkflow(session_manager)
    
    workflow_result = workflow_manager.start_workflow(
        test_user, 
        "Create secure authentication system",
        {"project": "AHSSI", "urgency": "high"}
    )
    
    if workflow_result["success"]:
        print(f"  ✅ Started workflow: {workflow_result['workflow_id']}")
        print(f"  📝 PM Session: {workflow_result['sessions']['pm_session_id']}")
        print(f"  🔍 Tech Lead Session: {workflow_result['sessions']['tech_lead_session_id']}")
        print(f"  🎯 Jira Creator Session: {workflow_result['sessions']['jira_creator_session_id']}")
    
    # Test session analytics
    print("\n📊 Session Analytics:")
    analytics = session_manager.get_session_analytics()
    print(f"  Active Sessions: {analytics['active_sessions']}")
    print(f"  Total Users: {analytics['total_users']}")
    print(f"  Registered Agents: {analytics['registered_agents']}")
    
    # Test session cleanup
    print("\n🧹 Testing session cleanup...")
    cleaned = session_manager.cleanup_expired_sessions()
    print(f"  Cleaned up {cleaned} expired sessions")
    
    print("\n✅ Session management testing complete!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)