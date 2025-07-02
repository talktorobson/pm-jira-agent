#!/usr/bin/env python3

"""
Production Server for PM Jira Agent Multi-Agent System
Cloud Run deployment with FastAPI and comprehensive monitoring
"""

import os
import time
import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from orchestrator import MultiAgentOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PM Jira Agent API",
    description="Multi-Agent Jira Ticket Creation System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
PROJECT_ID = os.getenv("PROJECT_ID", "service-execution-uat-bb7")
LOCATION = os.getenv("LOCATION", "europe-west9")

try:
    orchestrator = MultiAgentOrchestrator(PROJECT_ID, LOCATION)
    logger.info("Multi-Agent Orchestrator initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize orchestrator: {str(e)}")
    orchestrator = None

# Request/Response models
class TicketRequest(BaseModel):
    user_request: str = Field(..., description="User's ticket request", min_length=10, max_length=1000)
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context information")
    priority: Optional[str] = Field("Medium", description="Ticket priority")
    issue_type: Optional[str] = Field("Story", description="Jira issue type")

class TicketResponse(BaseModel):
    success: bool
    workflow_id: Optional[str] = None
    ticket_created: Optional[bool] = None
    ticket_key: Optional[str] = None
    ticket_url: Optional[str] = None
    quality_score: Optional[float] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None
    workflow_statistics: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    orchestrator_status: str
    uptime_seconds: float

# Global variables for monitoring
app_start_time = time.time()
request_count = 0
success_count = 0
error_count = 0

@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    """Middleware for request monitoring and logging"""
    global request_count
    request_count += 1
    
    start_time = time.time()
    request_id = f"req_{int(start_time)}"
    
    logger.info(f"Request {request_id}: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        execution_time = time.time() - start_time
        
        logger.info(f"Request {request_id} completed: {response.status_code} ({execution_time:.2f}s)")
        return response
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Request {request_id} failed: {str(e)} ({execution_time:.2f}s)")
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring and load balancer"""
    global app_start_time
    
    uptime = time.time() - app_start_time
    orchestrator_status = "healthy" if orchestrator else "unhealthy"
    
    return HealthResponse(
        status="healthy" if orchestrator else "degraded",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        orchestrator_status=orchestrator_status,
        uptime_seconds=round(uptime, 2)
    )

@app.get("/metrics")
async def get_metrics():
    """Metrics endpoint for monitoring"""
    global request_count, success_count, error_count, app_start_time
    
    uptime = time.time() - app_start_time
    success_rate = (success_count / request_count * 100) if request_count > 0 else 0
    
    return {
        "uptime_seconds": round(uptime, 2),
        "total_requests": request_count,
        "successful_requests": success_count,
        "failed_requests": error_count,
        "success_rate_percent": round(success_rate, 2),
        "orchestrator_available": orchestrator is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/create-ticket", response_model=TicketResponse)
async def create_jira_ticket(request: TicketRequest):
    """Create Jira ticket using multi-agent workflow"""
    global success_count, error_count
    
    if not orchestrator:
        error_count += 1
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Multi-agent orchestrator not available"
        )
    
    start_time = time.time()
    workflow_id = f"api_workflow_{int(start_time)}"
    
    try:
        logger.info(f"Starting workflow {workflow_id} for request: {request.user_request[:100]}...")
        
        # Prepare context
        context = request.context or {}
        context.update({
            "priority": request.priority,
            "issue_type": request.issue_type,
            "api_request": True,
            "request_timestamp": datetime.now().isoformat()
        })
        
        # Execute multi-agent workflow
        result = orchestrator.create_jira_ticket(request.user_request, context)
        execution_time = time.time() - start_time
        
        if result["success"]:
            success_count += 1
            logger.info(f"Workflow {workflow_id} completed successfully in {execution_time:.2f}s")
            
            return TicketResponse(
                success=True,
                workflow_id=result.get("workflow_id"),
                ticket_created=result.get("ticket_created"),
                ticket_key=result.get("ticket_key"),
                ticket_url=result.get("ticket_url"),
                quality_score=result.get("workflow_statistics", {}).get("quality_score_range", {}).get("final"),
                execution_time=round(execution_time, 2),
                workflow_statistics=result.get("workflow_statistics")
            )
        else:
            error_count += 1
            logger.error(f"Workflow {workflow_id} failed: {result.get('error', 'Unknown error')}")
            
            return TicketResponse(
                success=False,
                workflow_id=result.get("workflow_id"),
                ticket_created=False,
                execution_time=round(execution_time, 2),
                error=result.get("failure_reason", "Workflow execution failed")
            )
            
    except Exception as e:
        error_count += 1
        execution_time = time.time() - start_time
        
        logger.error(f"Workflow {workflow_id} exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get status of a specific workflow"""
    if not orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Multi-agent orchestrator not available"
        )
    
    try:
        status_info = orchestrator.get_workflow_status(workflow_id)
        return status_info
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "PM Jira Agent Multi-Agent System",
        "version": "1.0.0",
        "status": "healthy" if orchestrator else "degraded",
        "endpoints": {
            "create_ticket": "/create-ticket",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        },
        "description": "AI-powered Jira ticket creation using multi-agent workflows"
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    global error_count
    error_count += 1
    
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    
    logger.info(f"Starting PM Jira Agent Production Server on port {port}")
    logger.info(f"Project: {PROJECT_ID}, Location: {LOCATION}")
    
    uvicorn.run(
        "production_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        workers=1,  # Single worker for development, scale as needed
        timeout_keep_alive=30,
        timeout_graceful_shutdown=10
    )