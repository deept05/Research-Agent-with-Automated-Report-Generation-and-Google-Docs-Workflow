"""
State management for LangGraph research workflow.
"""
from typing import TypedDict, List, Optional, Dict, Any
from datetime import datetime


class ResearchState(TypedDict):
    """
    State object shared across all nodes in the research graph.
    This state is passed between nodes and maintains the workflow state.
    """
    # Input
    query: str
    job_id: str
    user_id: Optional[str]
    max_results: int
    include_citations: bool
    
    # Search results
    raw_search_results: List[Dict[str, Any]]
    filtered_results: List[Dict[str, Any]]
    
    # Content
    extracted_content: List[Dict[str, str]]
    synthesized_content: str
    
    # Report components
    report_title: str
    executive_summary: str
    report_sections: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    
    # Final output
    report_markdown: str
    google_doc_url: Optional[str]
    n8n_response: Optional[Dict[str, Any]]
    
    # Workflow metadata
    current_step: str
    error_message: Optional[str]
    retry_count: int
    started_at: datetime
    completed_at: Optional[datetime]
    
    # Progress tracking
    progress_messages: List[str]


def create_initial_state(
    query: str,
    job_id: str,
    user_id: Optional[str] = None,
    max_results: int = 10,
    include_citations: bool = True
) -> ResearchState:
    """
    Create initial state for a research job.
    
    Args:
        query: Research query
        job_id: Unique job identifier
        user_id: Optional user identifier
        max_results: Maximum number of search results
        include_citations: Whether to include citations
        
    Returns:
        Initial research state
    """
    return ResearchState(
        # Input
        query=query,
        job_id=job_id,
        user_id=user_id,
        max_results=max_results,
        include_citations=include_citations,
        
        # Search results
        raw_search_results=[],
        filtered_results=[],
        
        # Content
        extracted_content=[],
        synthesized_content="",
        
        # Report components
        report_title="",
        executive_summary="",
        report_sections=[],
        citations=[],
        
        # Final output
        report_markdown="",
        google_doc_url=None,
        n8n_response=None,
        
        # Workflow metadata
        current_step="initialized",
        error_message=None,
        retry_count=0,
        started_at=datetime.now(),
        completed_at=None,
        
        # Progress tracking
        progress_messages=[]
    )