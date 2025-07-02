#!/usr/bin/env python3

"""
Monitoring and Analytics Module - Phase 3
Comprehensive monitoring, metrics collection, and analytics for the multi-agent system
"""

import time
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from google.cloud import monitoring_v3
from google.cloud import logging as cloud_logging

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics to track"""
    WORKFLOW_SUCCESS = "workflow_success"
    WORKFLOW_FAILURE = "workflow_failure"
    QUALITY_SCORE = "quality_score"
    EXECUTION_TIME = "execution_time"
    AGENT_PERFORMANCE = "agent_performance"
    BUSINESS_RULES_APPLIED = "business_rules_applied"
    API_REQUESTS = "api_requests"
    ERROR_RATE = "error_rate"

@dataclass
class WorkflowMetrics:
    """Workflow execution metrics"""
    workflow_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    quality_score: float = 0.0
    iteration_count: int = 0
    agent_execution_times: Dict[str, float] = None
    business_rules_applied: List[str] = None
    error_message: Optional[str] = None
    ticket_created: bool = False
    ticket_key: Optional[str] = None

@dataclass
class AgentMetrics:
    """Individual agent performance metrics"""
    agent_name: str
    execution_time: float
    success: bool
    quality_score: Optional[float] = None
    iteration: int = 1
    error_message: Optional[str] = None

class MonitoringSystem:
    """Comprehensive monitoring and analytics system"""
    
    def __init__(self, project_id: str = "service-execution-uat-bb7"):
        self.project_id = project_id
        
        # Initialize Google Cloud Monitoring
        try:
            self.monitoring_client = monitoring_v3.MetricServiceClient()
            self.logging_client = cloud_logging.Client(project=project_id)
            self.project_name = f"projects/{project_id}"
            
            # Set up structured logging
            self.logging_client.setup_logging()
            
            logger.info("Monitoring system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize monitoring: {str(e)}")
            self.monitoring_client = None
            self.logging_client = None
        
        # In-memory metrics store (for development/testing)
        self.metrics_store = {
            "workflows": [],
            "agents": [],
            "api_requests": [],
            "errors": []
        }
        
        # Performance thresholds
        self.thresholds = {
            "quality_score_minimum": 0.8,
            "execution_time_maximum": 30.0,  # seconds
            "error_rate_maximum": 0.05,  # 5%
            "success_rate_minimum": 0.95  # 95%
        }
    
    def start_workflow_monitoring(self, workflow_id: str, user_request: str) -> Dict[str, Any]:
        """Start monitoring a new workflow"""
        
        workflow_metrics = WorkflowMetrics(
            workflow_id=workflow_id,
            start_time=datetime.now(),
            agent_execution_times={},
            business_rules_applied=[]
        )
        
        # Store in memory
        self.metrics_store["workflows"].append(workflow_metrics)
        
        # Log workflow start
        self._log_structured_event("workflow_started", {
            "workflow_id": workflow_id,
            "user_request_length": len(user_request),
            "timestamp": workflow_metrics.start_time.isoformat()
        })
        
        logger.info(f"Started monitoring workflow {workflow_id}")
        
        return {
            "workflow_id": workflow_id,
            "monitoring_started": True,
            "start_time": workflow_metrics.start_time.isoformat()
        }
    
    def track_agent_execution(self, workflow_id: str, agent_name: str, 
                            execution_time: float, success: bool, 
                            quality_score: Optional[float] = None, 
                            iteration: int = 1, 
                            error_message: Optional[str] = None) -> None:
        """Track individual agent execution metrics"""
        
        agent_metrics = AgentMetrics(
            agent_name=agent_name,
            execution_time=execution_time,
            success=success,
            quality_score=quality_score,
            iteration=iteration,
            error_message=error_message
        )
        
        # Store in memory
        self.metrics_store["agents"].append(agent_metrics)
        
        # Update workflow metrics
        workflow_metrics = self._find_workflow_metrics(workflow_id)
        if workflow_metrics:
            workflow_metrics.agent_execution_times[agent_name] = execution_time
            if quality_score:
                workflow_metrics.quality_score = max(workflow_metrics.quality_score, quality_score)
        
        # Log agent execution
        self._log_structured_event("agent_execution", {
            "workflow_id": workflow_id,
            "agent_name": agent_name,
            "execution_time": execution_time,
            "success": success,
            "quality_score": quality_score,
            "iteration": iteration,
            "error_message": error_message
        })
        
        # Send metrics to Google Cloud Monitoring
        self._send_custom_metric(MetricType.AGENT_PERFORMANCE, {
            "agent_name": agent_name,
            "execution_time": execution_time,
            "success": success
        })
        
        if not success:
            self._send_custom_metric(MetricType.WORKFLOW_FAILURE, {
                "agent_name": agent_name,
                "error_message": error_message
            })
    
    def track_business_rules(self, workflow_id: str, rules_applied: List[str], 
                           execution_time: float) -> None:
        """Track business rules application"""
        
        # Update workflow metrics
        workflow_metrics = self._find_workflow_metrics(workflow_id)
        if workflow_metrics:
            workflow_metrics.business_rules_applied.extend(rules_applied)
        
        # Log business rules application
        self._log_structured_event("business_rules_applied", {
            "workflow_id": workflow_id,
            "rules_applied": rules_applied,
            "execution_time": execution_time,
            "rule_count": len(rules_applied)
        })
        
        # Send metrics
        self._send_custom_metric(MetricType.BUSINESS_RULES_APPLIED, {
            "rule_count": len(rules_applied),
            "execution_time": execution_time
        })
    
    def complete_workflow_monitoring(self, workflow_id: str, success: bool, 
                                   ticket_created: bool = False, 
                                   ticket_key: Optional[str] = None,
                                   error_message: Optional[str] = None) -> Dict[str, Any]:
        """Complete workflow monitoring and calculate final metrics"""
        
        workflow_metrics = self._find_workflow_metrics(workflow_id)
        if not workflow_metrics:
            logger.error(f"Workflow metrics not found for {workflow_id}")
            return {"error": "Workflow metrics not found"}
        
        # Update final metrics
        workflow_metrics.end_time = datetime.now()
        workflow_metrics.success = success
        workflow_metrics.ticket_created = ticket_created
        workflow_metrics.ticket_key = ticket_key
        workflow_metrics.error_message = error_message
        
        # Calculate total execution time
        total_execution_time = (workflow_metrics.end_time - workflow_metrics.start_time).total_seconds()
        
        # Log workflow completion
        self._log_structured_event("workflow_completed", {
            "workflow_id": workflow_id,
            "success": success,
            "total_execution_time": total_execution_time,
            "quality_score": workflow_metrics.quality_score,
            "iteration_count": workflow_metrics.iteration_count,
            "ticket_created": ticket_created,
            "ticket_key": ticket_key,
            "business_rules_applied": workflow_metrics.business_rules_applied,
            "error_message": error_message
        })
        
        # Send final metrics
        if success:
            self._send_custom_metric(MetricType.WORKFLOW_SUCCESS, {
                "execution_time": total_execution_time,
                "quality_score": workflow_metrics.quality_score
            })
        else:
            self._send_custom_metric(MetricType.WORKFLOW_FAILURE, {
                "error_message": error_message
            })
        
        self._send_custom_metric(MetricType.EXECUTION_TIME, {
            "total_time": total_execution_time
        })
        
        self._send_custom_metric(MetricType.QUALITY_SCORE, {
            "score": workflow_metrics.quality_score
        })
        
        # Check against thresholds and alert if needed
        alerts = self._check_thresholds(workflow_metrics, total_execution_time)
        
        return {
            "workflow_id": workflow_id,
            "monitoring_completed": True,
            "total_execution_time": total_execution_time,
            "final_metrics": asdict(workflow_metrics),
            "alerts": alerts
        }
    
    def track_api_request(self, endpoint: str, method: str, status_code: int, 
                         response_time: float, user_agent: Optional[str] = None) -> None:
        """Track API request metrics"""
        
        api_metrics = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "user_agent": user_agent
        }
        
        # Store in memory
        self.metrics_store["api_requests"].append(api_metrics)
        
        # Log API request
        self._log_structured_event("api_request", api_metrics)
        
        # Send metrics
        self._send_custom_metric(MetricType.API_REQUESTS, {
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time": response_time
        })
    
    def get_analytics_dashboard(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Generate analytics dashboard data"""
        
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_range_hours)
            
            # Filter workflows in time range
            recent_workflows = [
                w for w in self.metrics_store["workflows"]
                if w.start_time >= start_time
            ]
            
            # Calculate aggregate metrics
            total_workflows = len(recent_workflows)
            successful_workflows = len([w for w in recent_workflows if w.success])
            success_rate = (successful_workflows / total_workflows * 100) if total_workflows > 0 else 0
            
            # Calculate average metrics
            completed_workflows = [w for w in recent_workflows if w.end_time]
            avg_execution_time = 0
            avg_quality_score = 0
            
            if completed_workflows:
                execution_times = [
                    (w.end_time - w.start_time).total_seconds() 
                    for w in completed_workflows
                ]
                avg_execution_time = sum(execution_times) / len(execution_times)
                
                quality_scores = [w.quality_score for w in completed_workflows if w.quality_score > 0]
                avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Agent performance analysis
            recent_agents = [
                a for a in self.metrics_store["agents"]
            ]
            
            agent_performance = {}
            for agent in recent_agents:
                if agent.agent_name not in agent_performance:
                    agent_performance[agent.agent_name] = {
                        "executions": 0,
                        "successes": 0,
                        "total_time": 0,
                        "avg_time": 0,
                        "success_rate": 0
                    }
                
                perf = agent_performance[agent.agent_name]
                perf["executions"] += 1
                if agent.success:
                    perf["successes"] += 1
                perf["total_time"] += agent.execution_time
            
            # Calculate agent averages
            for agent_name, perf in agent_performance.items():
                perf["avg_time"] = perf["total_time"] / perf["executions"]
                perf["success_rate"] = (perf["successes"] / perf["executions"] * 100)
            
            # Business rules analysis
            all_rules = []
            for workflow in recent_workflows:
                all_rules.extend(workflow.business_rules_applied or [])
            
            rule_frequency = {}
            for rule in all_rules:
                rule_frequency[rule] = rule_frequency.get(rule, 0) + 1
            
            return {
                "time_range_hours": time_range_hours,
                "summary": {
                    "total_workflows": total_workflows,
                    "successful_workflows": successful_workflows,
                    "success_rate_percent": round(success_rate, 2),
                    "average_execution_time_seconds": round(avg_execution_time, 2),
                    "average_quality_score": round(avg_quality_score, 2)
                },
                "agent_performance": agent_performance,
                "business_rules_frequency": rule_frequency,
                "thresholds": self.thresholds,
                "status": "healthy" if success_rate >= 95 else "degraded"
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics dashboard: {str(e)}")
            return {"error": str(e)}
    
    def _find_workflow_metrics(self, workflow_id: str) -> Optional[WorkflowMetrics]:
        """Find workflow metrics by ID"""
        for workflow in self.metrics_store["workflows"]:
            if workflow.workflow_id == workflow_id:
                return workflow
        return None
    
    def _log_structured_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log structured event for analysis"""
        
        structured_log = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "service": "pm-jira-agent",
            "version": "1.0.0",
            **data
        }
        
        # Log to Google Cloud Logging if available
        if self.logging_client:
            try:
                logger.info(json.dumps(structured_log))
            except Exception as e:
                logger.error(f"Failed to send structured log: {str(e)}")
        else:
            # Fallback to standard logging
            logger.info(f"[{event_type}] {json.dumps(data)}")
    
    def _send_custom_metric(self, metric_type: MetricType, data: Dict[str, Any]) -> None:
        """Send custom metric to Google Cloud Monitoring"""
        
        if not self.monitoring_client:
            return
        
        try:
            # Create custom metric (simplified implementation)
            # In production, you would create proper metric descriptors and time series
            logger.debug(f"Metric [{metric_type.value}]: {json.dumps(data)}")
            
        except Exception as e:
            logger.error(f"Failed to send metric {metric_type.value}: {str(e)}")
    
    def _check_thresholds(self, workflow_metrics: WorkflowMetrics, 
                         total_execution_time: float) -> List[Dict[str, Any]]:
        """Check metrics against thresholds and generate alerts"""
        
        alerts = []
        
        # Check quality score threshold
        if workflow_metrics.quality_score < self.thresholds["quality_score_minimum"]:
            alerts.append({
                "type": "quality_score_low",
                "message": f"Quality score {workflow_metrics.quality_score} below threshold {self.thresholds['quality_score_minimum']}",
                "severity": "warning"
            })
        
        # Check execution time threshold
        if total_execution_time > self.thresholds["execution_time_maximum"]:
            alerts.append({
                "type": "execution_time_high",
                "message": f"Execution time {total_execution_time}s exceeds threshold {self.thresholds['execution_time_maximum']}s",
                "severity": "warning"
            })
        
        # Check workflow success
        if not workflow_metrics.success:
            alerts.append({
                "type": "workflow_failure",
                "message": f"Workflow failed: {workflow_metrics.error_message}",
                "severity": "error"
            })
        
        return alerts


# Export the monitoring system
__all__ = ["MonitoringSystem", "WorkflowMetrics", "AgentMetrics", "MetricType"]