"""
API routes for research agent.
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from typing import Dict, Any
import uuid
from datetime import datetime

from app.models.schemas import (
    ResearchRequest,
    ResearchResponse,
    JobStatusResponse,
    HealthResponse,
    ResearchStatus
)
# Import research agent components lazily inside functions to avoid heavy
# import-time dependencies (langgraph/langsmith) which can cause startup
# failures when optional packages have incompatible versions.
from app.utils.logger import app_logger

# Router instance
router = APIRouter()

# In-memory job storage (use database in production)
jobs_db: Dict[str, Dict[str, Any]] = {}


async def process_research_job(job_id: str, state: Dict[str, Any]):
    """
    Background task to process research job.
    
    Args:
        job_id: Job identifier
        state: Initial research state
    """
    try:
        app_logger.info(f"Starting research job {job_id}")
        
        # Update job status
        jobs_db[job_id]["status"] = ResearchStatus.PROCESSING
        
        # Execute research workflow (lazy import)
        from app.research_agent.graph import research_graph

        result = research_graph.invoke(state)

        # Create Google Doc (lazy import)
        try:
            from app.services.google_docs import google_docs_service
        except Exception:
            google_docs_service = None

        if google_docs_service:
            try:
                doc_result = google_docs_service.create_document(
                    title=result.get("report_title", f"Research Report - {job_id}"),
                    content=result.get("report_markdown", "")
                )
            except Exception:
                doc_result = None
        else:
            doc_result = None

        if doc_result:
            result["google_doc_url"] = doc_result.get("url")

            # Trigger n8n workflow (lazy import)
            try:
                from app.services.n8n_client import n8n_client
            except Exception:
                n8n_client = None

            if n8n_client:
                try:
                    n8n_response = await n8n_client.trigger_workflow(
                        job_id=job_id,
                        google_doc_url=doc_result.get("url"),
                        report_data={
                            "title": result.get("report_title", ""),
                            "query": result.get("query", ""),
                            "created_at": str(result.get("started_at", "")),
                            "user_id": result.get("user_id", ""),
                            "citations": result.get("citations", []),
                            "summary": result.get("executive_summary", "")
                        }
                    )
                except Exception:
                    n8n_response = None

                result["n8n_response"] = n8n_response
        
        # Update job with results
        jobs_db[job_id].update({
            "status": ResearchStatus.COMPLETED,
            "completed_at": datetime.now(),
            "google_doc_url": result.get("google_doc_url"),
            "summary": result.get("executive_summary", ""),
            "report_data": result
        })
        
        app_logger.info(f"Research job {job_id} completed successfully")
        
    except Exception as e:
        app_logger.error(f"Error processing job {job_id}: {str(e)}")
        jobs_db[job_id].update({
            "status": ResearchStatus.FAILED,
            "completed_at": datetime.now(),
            "error_message": str(e)
        })


@router.post("/research", response_model=ResearchResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_research_job(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a new research query.
    
    Args:
        request: Research request
        background_tasks: FastAPI background tasks
        
    Returns:
        Research job response with job ID
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        app_logger.info(f"Creating research job {job_id} for query: {request.query}")
        
        # Create initial state (imported lazily)
        from app.research_agent.state import create_initial_state

        initial_state = create_initial_state(
            query=request.query,
            job_id=job_id,
            user_id=request.user_id,
            max_results=request.max_results,
            include_citations=request.include_citations
        )
        
        # Store job
        jobs_db[job_id] = {
            "job_id": job_id,
            "status": ResearchStatus.PENDING,
            "query": request.query,
            "created_at": datetime.now(),
            "completed_at": None,
            "google_doc_url": None,
            "summary": None,
            "error_message": None
        }
        
        # Add to background tasks
        background_tasks.add_task(process_research_job, job_id, initial_state)
        
        return ResearchResponse(**jobs_db[job_id])
        
    except Exception as e:
        app_logger.error(f"Error creating research job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create research job: {str(e)}"
        )


@router.get("/research/{job_id}", response_model=ResearchResponse)
async def get_research_job(job_id: str):
    """
    Get research job status and results.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Research job details
    """
    if job_id not in jobs_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return ResearchResponse(**jobs_db[job_id])


@router.get("/research/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get research job status only.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status information
    """
    if job_id not in jobs_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    job = jobs_db[job_id]
    
    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job.get("report_data", {}).get("current_step") if job.get("report_data") else None,
        google_doc_url=job.get("google_doc_url"),
        error_message=job.get("error_message")
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    # Lazy-check optional services
    try:
        from app.services.google_docs import google_docs_service
        google_docs_ok = getattr(google_docs_service, "docs_service", None) is not None
    except Exception:
        google_docs_ok = False

    try:
        from app.services.n8n_client import n8n_client
        n8n_ok = bool(getattr(n8n_client, "webhook_url", None))
    except Exception:
        n8n_ok = False

    services_status = {
        "google_docs": google_docs_ok,
        "n8n": n8n_ok,
        "llm": True  # LLM is considered available if configured
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        services=services_status
    )


@router.get("/jobs", response_model=Dict[str, Any])
async def list_jobs(limit: int = 10, offset: int = 0):
    """
    List all research jobs.
    
    Args:
        limit: Maximum number of jobs to return
        offset: Offset for pagination
        
    Returns:
        List of jobs
    """
    jobs_list = list(jobs_db.values())
    total = len(jobs_list)
    
    # Sort by created_at desc
    jobs_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Paginate
    paginated_jobs = jobs_list[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "jobs": paginated_jobs
    }