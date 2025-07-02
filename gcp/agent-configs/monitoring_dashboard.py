#!/usr/bin/env python3

"""
Vertex AI Agent Engine Monitoring Dashboard
Comprehensive monitoring and observability for deployed agents
Based on latest Google Cloud monitoring best practices
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from google.cloud import monitoring_v3
from google.cloud import logging as cloud_logging
import vertexai
from vertexai.preview import agent_engines

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    resource_name: str
    display_name: str
    request_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_latency_ms: float = 0.0
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    last_update: datetime = None

@dataclass
class CustomMetric:
    """Custom metric definition"""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: datetime
    unit: str = ""

class VertexAIMonitoringDashboard:
    """Comprehensive monitoring dashboard for Vertex AI Agent Engine"""
    
    def __init__(self, project_id: str = "service-execution-uat-bb7", location: str = "europe-west9"):
        self.project_id = project_id
        self.location = location
        
        # Initialize clients
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.logging_client = cloud_logging.Client(project=project_id)
        self.project_name = f"projects/{project_id}"
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Custom metrics store
        self.custom_metrics = []
        
        logger.info(f"Monitoring dashboard initialized for project {project_id}")
    
    def get_agent_metrics(self, agent_resource_name: str, time_range_hours: int = 1) -> AgentMetrics:
        """Get comprehensive metrics for a specific agent"""
        
        try:
            # Get agent details
            agent = agent_engines.get(agent_resource_name)
            
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_range_hours)
            
            # Initialize metrics
            metrics = AgentMetrics(
                resource_name=agent_resource_name,
                display_name=agent.display_name,
                last_update=datetime.now()
            )
            
            # Get built-in metrics
            metrics = self._fetch_builtin_metrics(metrics, start_time, end_time)
            
            # Get custom metrics
            metrics = self._fetch_custom_metrics(metrics, start_time, end_time)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics for agent {agent_resource_name}: {str(e)}")
            return AgentMetrics(
                resource_name=agent_resource_name,
                display_name="Unknown",
                last_update=datetime.now()
            )
    
    def get_all_agents_metrics(self, time_range_hours: int = 1) -> List[AgentMetrics]:
        """Get metrics for all deployed agents"""
        
        try:
            # List all agents
            agents = agent_engines.list()
            
            # Get metrics for each agent
            all_metrics = []
            for agent in agents:
                metrics = self.get_agent_metrics(agent.resource_name, time_range_hours)
                all_metrics.append(metrics)
            
            return all_metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics for all agents: {str(e)}")
            return []
    
    def create_custom_metric_descriptor(self, metric_name: str, description: str, 
                                      value_type: str = "DOUBLE", 
                                      metric_kind: str = "GAUGE") -> bool:
        """Create custom metric descriptor"""
        
        try:
            descriptor = monitoring_v3.MetricDescriptor(
                type=f"custom.googleapis.com/vertex_ai_agent/{metric_name}",
                metric_kind=getattr(monitoring_v3.MetricDescriptor.MetricKind, metric_kind),
                value_type=getattr(monitoring_v3.MetricDescriptor.ValueType, value_type),
                description=description,
                display_name=metric_name.replace("_", " ").title(),
                labels=[
                    monitoring_v3.LabelDescriptor(
                        key="agent_name",
                        value_type=monitoring_v3.LabelDescriptor.ValueType.STRING,
                        description="Name of the agent"
                    ),
                    monitoring_v3.LabelDescriptor(
                        key="resource_name", 
                        value_type=monitoring_v3.LabelDescriptor.ValueType.STRING,
                        description="Resource name of the agent"
                    )
                ]
            )
            
            self.monitoring_client.create_metric_descriptor(
                name=self.project_name,
                metric_descriptor=descriptor
            )
            
            logger.info(f"✅ Created custom metric descriptor: {metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create metric descriptor {metric_name}: {str(e)}")
            return False
    
    def write_custom_metric(self, metric: CustomMetric) -> bool:
        """Write custom metric to Cloud Monitoring"""
        
        try:
            # Create time series data
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/vertex_ai_agent/{metric.name}"
            
            # Add labels
            for key, value in metric.labels.items():
                series.metric.labels[key] = value
            
            # Set resource
            series.resource.type = "gce_instance"  # or appropriate resource type
            series.resource.labels["instance_id"] = "vertex-ai-agent"
            series.resource.labels["zone"] = f"{self.location}-a"
            
            # Create data point
            point = monitoring_v3.Point()
            point.value.double_value = metric.value
            point.interval.end_time.seconds = int(metric.timestamp.timestamp())
            series.points = [point]
            
            # Write to Cloud Monitoring
            self.monitoring_client.create_time_series(
                name=self.project_name,
                time_series=[series]
            )
            
            # Store locally
            self.custom_metrics.append(metric)
            
            logger.debug(f"✅ Written custom metric: {metric.name} = {metric.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to write custom metric {metric.name}: {str(e)}")
            return False
    
    def track_agent_request(self, agent_resource_name: str, agent_name: str, 
                          latency_ms: float, success: bool) -> None:
        """Track individual agent request"""
        
        timestamp = datetime.now()
        
        # Track request latency
        latency_metric = CustomMetric(
            name="request_latency",
            value=latency_ms,
            labels={
                "agent_name": agent_name,
                "resource_name": agent_resource_name
            },
            timestamp=timestamp,
            unit="ms"
        )
        self.write_custom_metric(latency_metric)
        
        # Track success/failure
        success_metric = CustomMetric(
            name="request_success",
            value=1.0 if success else 0.0,
            labels={
                "agent_name": agent_name,
                "resource_name": agent_resource_name,
                "status": "success" if success else "failure"
            },
            timestamp=timestamp
        )
        self.write_custom_metric(success_metric)
        
        # Track request count
        count_metric = CustomMetric(
            name="request_count",
            value=1.0,
            labels={
                "agent_name": agent_name,
                "resource_name": agent_resource_name
            },
            timestamp=timestamp
        )
        self.write_custom_metric(count_metric)
    
    def track_workflow_quality(self, workflow_id: str, quality_score: float, 
                             iteration_count: int, business_rules_applied: List[str]) -> None:
        """Track workflow quality metrics"""
        
        timestamp = datetime.now()
        
        # Track quality score
        quality_metric = CustomMetric(
            name="workflow_quality_score",
            value=quality_score,
            labels={
                "workflow_id": workflow_id
            },
            timestamp=timestamp
        )
        self.write_custom_metric(quality_metric)
        
        # Track iteration count
        iteration_metric = CustomMetric(
            name="workflow_iterations",
            value=float(iteration_count),
            labels={
                "workflow_id": workflow_id
            },
            timestamp=timestamp
        )
        self.write_custom_metric(iteration_metric)
        
        # Track business rules usage
        rules_metric = CustomMetric(
            name="business_rules_count",
            value=float(len(business_rules_applied)),
            labels={
                "workflow_id": workflow_id,
                "rules": ",".join(business_rules_applied)
            },
            timestamp=timestamp
        )
        self.write_custom_metric(rules_metric)
    
    def create_alerting_policy(self, metric_name: str, threshold: float, 
                             comparison: str = "COMPARISON_GREATER_THAN") -> bool:
        """Create alerting policy for custom metric"""
        
        try:
            # Define condition
            condition = monitoring_v3.AlertPolicy.Condition(
                display_name=f"High {metric_name.replace('_', ' ').title()}",
                condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                    filter=f'metric.type="custom.googleapis.com/vertex_ai_agent/{metric_name}"',
                    comparison=getattr(monitoring_v3.ComparisonType, comparison),
                    threshold_value=threshold,
                    duration={"seconds": 300},  # 5 minutes
                    aggregations=[
                        monitoring_v3.Aggregation(
                            alignment_period={"seconds": 300},
                            per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN
                        )
                    ]
                )
            )
            
            # Create policy
            policy = monitoring_v3.AlertPolicy(
                display_name=f"Vertex AI Agent {metric_name.replace('_', ' ').title()} Alert",
                conditions=[condition],
                combiner=monitoring_v3.AlertPolicy.ConditionCombinerType.OR,
                enabled=True,
                documentation=monitoring_v3.AlertPolicy.Documentation(
                    content=f"Alert when {metric_name} exceeds {threshold}",
                    mime_type="text/markdown"
                )
            )
            
            # Create in Cloud Monitoring
            self.monitoring_client.create_alert_policy(
                name=self.project_name,
                alert_policy=policy
            )
            
            logger.info(f"✅ Created alerting policy for {metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create alerting policy for {metric_name}: {str(e)}")
            return False
    
    def generate_dashboard_data(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive dashboard data"""
        
        try:
            # Get all agent metrics
            agent_metrics = self.get_all_agents_metrics(time_range_hours)
            
            # Calculate aggregate metrics
            total_requests = sum(m.request_count for m in agent_metrics)
            total_successes = sum(m.success_count for m in agent_metrics)
            total_failures = sum(m.failure_count for m in agent_metrics)
            
            overall_success_rate = (total_successes / total_requests * 100) if total_requests > 0 else 0
            avg_latency = sum(m.avg_latency_ms for m in agent_metrics) / len(agent_metrics) if agent_metrics else 0
            
            # Get recent custom metrics
            recent_metrics = [m for m in self.custom_metrics 
                           if m.timestamp >= datetime.now() - timedelta(hours=time_range_hours)]
            
            # Calculate quality metrics
            quality_scores = [m.value for m in recent_metrics if m.name == "workflow_quality_score"]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Business rules usage
            business_rules_metrics = [m for m in recent_metrics if m.name == "business_rules_count"]
            total_rules_applied = sum(m.value for m in business_rules_metrics)
            
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "time_range_hours": time_range_hours,
                "overview": {
                    "total_agents": len(agent_metrics),
                    "healthy_agents": len([m for m in agent_metrics if m.success_count > 0]),
                    "total_requests": total_requests,
                    "success_rate_percent": round(overall_success_rate, 2),
                    "average_latency_ms": round(avg_latency, 2),
                    "average_quality_score": round(avg_quality, 2)
                },
                "agent_details": [
                    {
                        "resource_name": m.resource_name,
                        "display_name": m.display_name,
                        "request_count": m.request_count,
                        "success_rate": round((m.success_count / m.request_count * 100) if m.request_count > 0 else 0, 2),
                        "avg_latency_ms": round(m.avg_latency_ms, 2),
                        "cpu_utilization": round(m.cpu_utilization, 2),
                        "memory_utilization": round(m.memory_utilization, 2),
                        "last_update": m.last_update.isoformat() if m.last_update else None
                    }
                    for m in agent_metrics
                ],
                "quality_metrics": {
                    "average_quality_score": round(avg_quality, 2),
                    "total_workflows": len([m for m in recent_metrics if m.name == "workflow_quality_score"]),
                    "quality_score_distribution": self._calculate_quality_distribution(quality_scores),
                    "business_rules_applied": int(total_rules_applied)
                },
                "performance_trends": self._calculate_performance_trends(recent_metrics),
                "health_status": self._calculate_health_status(agent_metrics, overall_success_rate)
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to generate dashboard data: {str(e)}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _fetch_builtin_metrics(self, metrics: AgentMetrics, start_time: datetime, end_time: datetime) -> AgentMetrics:
        """Fetch built-in Vertex AI Agent Engine metrics"""
        
        try:
            # This would fetch actual metrics from Cloud Monitoring
            # For now, simulate realistic metrics
            metrics.request_count = 150
            metrics.success_count = 142
            metrics.failure_count = 8
            metrics.avg_latency_ms = 1850.5
            metrics.cpu_utilization = 45.2
            metrics.memory_utilization = 62.8
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to fetch built-in metrics: {str(e)}")
            return metrics
    
    def _fetch_custom_metrics(self, metrics: AgentMetrics, start_time: datetime, end_time: datetime) -> AgentMetrics:
        """Fetch custom metrics for the agent"""
        
        try:
            # Filter metrics for this agent and time range
            agent_metrics = [
                m for m in self.custom_metrics
                if m.labels.get("resource_name") == metrics.resource_name
                and start_time <= m.timestamp <= end_time
            ]
            
            # Calculate averages and totals
            if agent_metrics:
                latency_metrics = [m.value for m in agent_metrics if m.name == "request_latency"]
                if latency_metrics:
                    metrics.avg_latency_ms = sum(latency_metrics) / len(latency_metrics)
                
                success_metrics = [m.value for m in agent_metrics if m.name == "request_success"]
                metrics.success_count = int(sum(success_metrics))
                metrics.failure_count = len(success_metrics) - metrics.success_count
                metrics.request_count = len(success_metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to fetch custom metrics: {str(e)}")
            return metrics
    
    def _calculate_quality_distribution(self, quality_scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of quality scores"""
        
        if not quality_scores:
            return {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        for score in quality_scores:
            if score >= 0.9:
                distribution["excellent"] += 1
            elif score >= 0.8:
                distribution["good"] += 1
            elif score >= 0.6:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1
        
        return distribution
    
    def _calculate_performance_trends(self, recent_metrics: List[CustomMetric]) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        
        # Group metrics by hour
        hourly_data = {}
        
        for metric in recent_metrics:
            hour_key = metric.timestamp.strftime("%Y-%m-%d %H:00")
            
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {
                    "requests": 0,
                    "successes": 0,
                    "latencies": [],
                    "quality_scores": []
                }
            
            if metric.name == "request_count":
                hourly_data[hour_key]["requests"] += metric.value
            elif metric.name == "request_success" and metric.value == 1.0:
                hourly_data[hour_key]["successes"] += 1
            elif metric.name == "request_latency":
                hourly_data[hour_key]["latencies"].append(metric.value)
            elif metric.name == "workflow_quality_score":
                hourly_data[hour_key]["quality_scores"].append(metric.value)
        
        # Calculate trends
        trends = []
        for hour, data in sorted(hourly_data.items()):
            success_rate = (data["successes"] / data["requests"] * 100) if data["requests"] > 0 else 0
            avg_latency = sum(data["latencies"]) / len(data["latencies"]) if data["latencies"] else 0
            avg_quality = sum(data["quality_scores"]) / len(data["quality_scores"]) if data["quality_scores"] else 0
            
            trends.append({
                "hour": hour,
                "requests": int(data["requests"]),
                "success_rate": round(success_rate, 2),
                "avg_latency_ms": round(avg_latency, 2),
                "avg_quality_score": round(avg_quality, 2)
            })
        
        return {"hourly_trends": trends}
    
    def _calculate_health_status(self, agent_metrics: List[AgentMetrics], overall_success_rate: float) -> str:
        """Calculate overall system health status"""
        
        if overall_success_rate >= 95:
            return "healthy"
        elif overall_success_rate >= 85:
            return "warning"
        else:
            return "critical"
    
    def setup_default_metrics_and_alerts(self) -> bool:
        """Set up default custom metrics and alerting policies"""
        
        try:
            logger.info("Setting up default metrics and alerts...")
            
            # Create custom metric descriptors
            metrics_to_create = [
                ("request_latency", "Request latency in milliseconds"),
                ("request_success", "Request success indicator (1.0 = success, 0.0 = failure)"),
                ("request_count", "Total number of requests"),
                ("workflow_quality_score", "Quality score for completed workflows"),
                ("workflow_iterations", "Number of iterations in workflow"),
                ("business_rules_count", "Number of business rules applied")
            ]
            
            for metric_name, description in metrics_to_create:
                self.create_custom_metric_descriptor(metric_name, description)
            
            # Create alerting policies
            alerts_to_create = [
                ("request_latency", 5000.0, "COMPARISON_GREATER_THAN"),  # Alert if latency > 5s
                ("request_success", 0.85, "COMPARISON_LESS_THAN"),       # Alert if success rate < 85%
                ("workflow_quality_score", 0.6, "COMPARISON_LESS_THAN")  # Alert if quality < 0.6
            ]
            
            for metric_name, threshold, comparison in alerts_to_create:
                self.create_alerting_policy(metric_name, threshold, comparison)
            
            logger.info("✅ Default metrics and alerts setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup default metrics and alerts: {str(e)}")
            return False

def main():
    """Main function for testing monitoring dashboard"""
    
    print("📊 Vertex AI Agent Engine Monitoring Dashboard")
    print("=" * 60)
    
    # Initialize dashboard
    dashboard = VertexAIMonitoringDashboard()
    
    # Setup default metrics and alerts
    print("\n🔧 Setting up monitoring infrastructure...")
    setup_success = dashboard.setup_default_metrics_and_alerts()
    
    if setup_success:
        print("✅ Monitoring infrastructure setup complete")
    else:
        print("⚠️ Some monitoring setup steps failed")
    
    # Generate sample metrics
    print("\n📈 Generating sample metrics...")
    sample_agents = [
        ("projects/123/locations/europe-west9/agents/pm-agent", "PM Agent"),
        ("projects/123/locations/europe-west9/agents/tech-lead-agent", "Tech Lead Agent"),
        ("projects/123/locations/europe-west9/agents/jira-creator-agent", "Jira Creator Agent")
    ]
    
    for resource_name, agent_name in sample_agents:
        # Simulate some requests
        for i in range(5):
            latency = 1500 + (i * 200)  # Varying latency
            success = i < 4  # 4/5 success rate
            dashboard.track_agent_request(resource_name, agent_name, latency, success)
    
    # Simulate workflow metrics
    dashboard.track_workflow_quality("workflow_001", 0.92, 2, ["security_rules", "gdpr_compliance"])
    dashboard.track_workflow_quality("workflow_002", 0.87, 1, ["performance_rules"])
    dashboard.track_workflow_quality("workflow_003", 0.95, 3, ["security_rules", "accessibility_rules"])
    
    # Generate dashboard
    print("\n📊 Generating dashboard data...")
    dashboard_data = dashboard.generate_dashboard_data(1)  # Last 1 hour
    
    print("\n📋 Dashboard Summary:")
    print(f"  Total Agents: {dashboard_data['overview']['total_agents']}")
    print(f"  Success Rate: {dashboard_data['overview']['success_rate_percent']}%")
    print(f"  Avg Latency: {dashboard_data['overview']['average_latency_ms']}ms")
    print(f"  Avg Quality Score: {dashboard_data['overview']['average_quality_score']}")
    print(f"  Health Status: {dashboard_data['health_status']}")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)