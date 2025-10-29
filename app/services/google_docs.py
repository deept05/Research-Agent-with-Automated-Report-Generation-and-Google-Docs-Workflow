"""
Google Docs integration service.
"""
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.utils.logger import app_logger
from app.config import settings
import os


class GoogleDocsService:
    """Service for creating and managing Google Docs."""
    
    def __init__(self):
        """Initialize Google Docs service."""
        self.credentials = None
        self.docs_service = None
        self.drive_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google API services."""
        try:
            if not settings.google_application_credentials:
                app_logger.warning("Google credentials not configured")
                return
            
            if not os.path.exists(settings.google_application_credentials):
                app_logger.warning(f"Credentials file not found: {settings.google_application_credentials}")
                return
            
            # Define the required scopes
            SCOPES = [
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/drive.file'
            ]
            
            # Load credentials
            self.credentials = service_account.Credentials.from_service_account_file(
                settings.google_application_credentials,
                scopes=SCOPES
            )
            
            # Build services
            self.docs_service = build('docs', 'v1', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            
            app_logger.info("Google Docs service initialized successfully")
            
        except Exception as e:
            app_logger.error(f"Error initializing Google Docs service: {str(e)}")
    
    def create_document(
        self,
        title: str,
        content: str,
        folder_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new Google Doc with the provided content.
        
        Args:
            title: Document title
            content: Document content (plain text or markdown)
            folder_id: Optional folder ID to place document in
            
        Returns:
            Dictionary with document_id and url, or None on failure
        """
        if not self.docs_service or not self.drive_service:
            app_logger.error("Google Docs service not initialized")
            return None
        
        try:
            app_logger.info(f"Creating Google Doc: {title}")
            
            # Create the document
            doc = self.docs_service.documents().create(body={'title': title}).execute()
            document_id = doc.get('documentId')
            
            app_logger.info(f"Document created with ID: {document_id}")
            
            # Insert content
            self._insert_content(document_id, content)
            
            # Move to folder if specified
            if folder_id or settings.google_docs_folder_id:
                target_folder = folder_id or settings.google_docs_folder_id
                self._move_to_folder(document_id, target_folder)
            
            # Make document accessible via link
            self._set_permissions(document_id)
            
            # Generate URL
            doc_url = f"https://docs.google.com/document/d/{document_id}/edit"
            
            app_logger.info(f"Google Doc created successfully: {doc_url}")
            
            return {
                "document_id": document_id,
                "url": doc_url,
                "title": title
            }
            
        except HttpError as e:
            app_logger.error(f"Google API error: {str(e)}")
            return None
        except Exception as e:
            app_logger.error(f"Error creating Google Doc: {str(e)}")
            return None
    
    def _insert_content(self, document_id: str, content: str):
        """
        Insert text content into the document.
        
        Args:
            document_id: Document ID
            content: Content to insert
        """
        try:
            # Convert markdown-style formatting to Google Docs format
            # For simplicity, we'll insert as plain text
            # You can enhance this to parse markdown and apply formatting
            
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': content
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            app_logger.info(f"Content inserted into document {document_id}")
            
        except Exception as e:
            app_logger.error(f"Error inserting content: {str(e)}")
    
    def _move_to_folder(self, document_id: str, folder_id: str):
        """
        Move document to a specific folder.
        
        Args:
            document_id: Document ID
            folder_id: Target folder ID
        """
        try:
            # Get current parents
            file = self.drive_service.files().get(
                fileId=document_id,
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(file.get('parents', []))
            
            # Move to new folder
            self.drive_service.files().update(
                fileId=document_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            
            app_logger.info(f"Document moved to folder {folder_id}")
            
        except Exception as e:
            app_logger.error(f"Error moving document to folder: {str(e)}")
    
    def _set_permissions(self, document_id: str):
        """
        Set document permissions to be accessible via link.
        
        Args:
            document_id: Document ID
        """
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.drive_service.permissions().create(
                fileId=document_id,
                body=permission
            ).execute()
            
            app_logger.info(f"Permissions set for document {document_id}")
            
        except Exception as e:
            app_logger.error(f"Error setting permissions: {str(e)}")


# Global service instance
google_docs_service = GoogleDocsService()