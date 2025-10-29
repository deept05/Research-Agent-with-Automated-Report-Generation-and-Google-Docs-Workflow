"""
LLM service wrapper for different providers.
"""
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.config import settings
from app.utils.logger import app_logger


class LLMService:
    """Wrapper service for LLM operations."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> ChatOpenAI:
        """
        Initialize the LLM client.
        
        Returns:
            Configured ChatOpenAI instance
        """
        try:
            llm = ChatOpenAI(
                model=self.model,
                temperature=0.3,
                api_key=self.api_key,
                max_retries=3
            )
            app_logger.info(f"LLM service initialized with model: {self.model}")
            return llm
        except Exception as e:
            app_logger.error(f"Error initializing LLM: {str(e)}")
            raise
    
    def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            temperature: Optional temperature override
            
        Returns:
            Generated text
        """
        try:
            messages = []
            
            if system_message:
                messages.append(SystemMessage(content=system_message))
            
            messages.append(HumanMessage(content=prompt))
            
            # Use custom temperature if provided
            if temperature is not None:
                llm = ChatOpenAI(
                    model=self.model,
                    temperature=temperature,
                    api_key=self.api_key
                )
                response = llm.invoke(messages)
            else:
                response = self.llm.invoke(messages)
            
            return response.content
            
        except Exception as e:
            app_logger.error(f"Error generating text: {str(e)}")
            raise
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        Summarize long text.
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length in words
            
        Returns:
            Summarized text
        """
        try:
            prompt = f"Summarize the following text in {max_length} words or less:\n\n{text}"
            system_message = "You are a professional summarizer. Create concise, informative summaries."
            
            return self.generate_text(prompt, system_message)
            
        except Exception as e:
            app_logger.error(f"Error summarizing text: {str(e)}")
            return text[:500] + "..."  # Fallback to truncation


# Global service instance
llm_service = LLMService()