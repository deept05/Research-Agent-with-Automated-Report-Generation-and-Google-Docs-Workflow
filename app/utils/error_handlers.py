"""
Error handling utilities.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.utils.logger import app_logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation exception
        
    Returns:
        JSON error response
    """
    app_logger.error(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "details": exc.errors(),
            "body": exc.body
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSON error response
    """
    app_logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "detail": str(exc) if app_logger.level == "DEBUG" else None
        }
    )


class ResearchAgentError(Exception):
    """Base exception for research agent errors."""
    pass


class SearchError(ResearchAgentError):
    """Exception raised for search errors."""
    pass


class ContentExtractionError(ResearchAgentError):
    """Exception raised for content extraction errors."""
    pass


class ReportGenerationError(ResearchAgentError):
    """Exception raised for report generation errors."""
    pass


class GoogleDocsError(ResearchAgentError):
    """Exception raised for Google Docs errors."""
    pass


class N8NError(ResearchAgentError):
    """Exception raised for n8n integration errors."""
    pass