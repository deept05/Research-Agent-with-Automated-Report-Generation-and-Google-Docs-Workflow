"""
Research tools for web search and content extraction.
"""
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import html2text
from app.utils.logger import app_logger
from app.config import settings


class WebSearchTool:
    """Tool for searching the web using DuckDuckGo."""
    
    def __init__(self):
        self.ddgs = DDGS()
        self.max_results = settings.max_search_results
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search the web for the given query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, and snippet
        """
        try:
            app_logger.info(f"Searching web for: {query}")
            results_limit = max_results or self.max_results
            
            results = []
            search_results = self.ddgs.text(query, max_results=results_limit)
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "source": result.get("href", "").split('/')[2] if result.get("href") else ""
                })
            
            app_logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            app_logger.error(f"Search error: {str(e)}")
            return []


class ContentExtractor:
    """Tool for extracting content from web pages."""
    
    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.max_content_length = settings.max_content_length
        self.timeout = 10
    
    def extract(self, url: str) -> Optional[Dict[str, str]]:
        """
        Extract text content from a URL.
        
        Args:
            url: URL to extract content from
            
        Returns:
            Dictionary with url and extracted text content
        """
        try:
            app_logger.info(f"Extracting content from: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            
            # Get text content
            text = self.html_converter.handle(str(soup))
            
            # Truncate if too long
            if len(text) > self.max_content_length:
                text = text[:self.max_content_length] + "..."
            
            app_logger.info(f"Extracted {len(text)} characters from {url}")
            
            return {
                "url": url,
                "content": text.strip()
            }
            
        except requests.Timeout:
            app_logger.warning(f"Timeout extracting content from: {url}")
            return None
        except requests.RequestException as e:
            app_logger.warning(f"Error extracting content from {url}: {str(e)}")
            return None
        except Exception as e:
            app_logger.error(f"Unexpected error extracting {url}: {str(e)}")
            return None
    
    def batch_extract(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Extract content from multiple URLs.
        
        Args:
            urls: List of URLs to extract from
            
        Returns:
            List of extracted content dictionaries
        """
        results = []
        for url in urls:
            content = self.extract(url)
            if content:
                results.append(content)
        
        return results


class RelevanceFilter:
    """Filter and rank search results by relevance."""
    
    def filter_results(
        self, 
        results: List[Dict[str, Any]], 
        query: str, 
        min_snippet_length: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Filter search results based on relevance criteria.
        
        Args:
            results: List of search results
            query: Original query for relevance checking
            min_snippet_length: Minimum snippet length to keep
            
        Returns:
            Filtered list of results
        """
        filtered = []
        query_terms = query.lower().split()
        
        for result in results:
            # Skip results with very short snippets
            if len(result.get("snippet", "")) < min_snippet_length:
                continue
            
            # Calculate simple relevance score based on query term matches
            snippet_lower = result.get("snippet", "").lower()
            title_lower = result.get("title", "").lower()
            
            score = sum(1 for term in query_terms if term in snippet_lower or term in title_lower)
            result["relevance_score"] = score
            
            filtered.append(result)
        
        # Sort by relevance score
        filtered.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        app_logger.info(f"Filtered to {len(filtered)} relevant results")
        return filtered