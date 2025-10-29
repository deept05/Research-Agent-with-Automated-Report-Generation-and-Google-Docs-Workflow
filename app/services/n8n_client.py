"""
n8n webhook client for workflow automation.
"""
from typing import Dict, Any, Optional
import aiohttp
import asyncio
from app.utils.logger import app_logger
from app.config import settings


class N8NClient:
    """Client for triggering n8n workflows via webhooks."""
    
    def __init__(self):
        """Initialize n8n client."""
        self.webhook_url = settings.n8n_webhook_url
        self.api_key = settings.n8n_api_key
        self.timeout = 30
    
    async def trigger_workflow(
        self,
        job_id: str,
        google_doc_url: str,
        report_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Trigger n8n workflow with research report data.
        
        Args:
            job_id: Research job ID
            google_doc_url: URL of the generated Google Doc
            report_data: Additional report metadata
            
        Returns:
            n8n response or None on failure
        """
        if not self.webhook_url:
            app_logger.warning("n8n webhook URL not configured")
            return None
        
        try:
            app_logger.info(f"Triggering n8n workflow for job {job_id}")
            
            # Prepare payload
            payload = {
                "job_id": job_id,
                "google_doc_url": google_doc_url,
                "report_title": report_data.get("title", ""),
                "query": report_data.get("query", ""),
                "created_at": report_data.get("created_at", ""),
                "user_id": report_data.get("user_id", ""),
                "citations_count": len(report_data.get("citations", [])),
                "summary": report_data.get("summary", "")
            }
            
            # Set headers
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Make async request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    response_data = await response.json()
                    
                    if response.status == 200:
                        app_logger.info(f"n8n workflow triggered successfully for job {job_id}")
                        return response_data
                    else:
                        app_logger.error(f"n8n workflow trigger failed: {response.status}")
                        return None
            
        except asyncio.TimeoutError:
            app_logger.error(f"n8n webhook timeout for job {job_id}")
            return None
        except aiohttp.ClientError as e:
            app_logger.error(f"n8n client error: {str(e)}")
            return None
        except Exception as e:
            app_logger.error(f"Error triggering n8n workflow: {str(e)}")
            return None
    
    def trigger_workflow_sync(
        self,
        job_id: str,
        google_doc_url: str,
        report_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Synchronous wrapper for triggering n8n workflow.
        
        Args:
            job_id: Research job ID
            google_doc_url: URL of the generated Google Doc
            report_data: Additional report metadata
            
        Returns:
            n8n response or None on failure
        """
        return asyncio.run(self.trigger_workflow(job_id, google_doc_url, report_data))


# Global client instance
n8n_client = N8NClient()