"""
LLM service wrapper for different providers.
"""
from typing import Optional, Dict, Any
try:
    # Preferred modern lightweight wrapper if installed
    from langchain_openai import ChatOpenAI  # type: ignore
except ModuleNotFoundError:
    # Fallback: implement a tiny compatibility wrapper around the `openai` package
    # to provide the minimal `ChatOpenAI(...).invoke(messages)` interface used
    # by the app. This avoids requiring the `langchain_openai` package.
    import openai

    class ChatOpenAI:
        def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.0, api_key: str | None = None, max_retries: int = 3, **kwargs):
            if api_key:
                openai.api_key = api_key
            self.model = model
            self.temperature = temperature
            self.max_retries = max_retries

        def invoke(self, messages):
            # Accept list of message-like objects; fall back to raw strings
            payload = []
            for m in messages:
                try:
                    role = getattr(m, 'type', None) or getattr(m, 'role', None)
                    # map SystemMessage/HumanMessage to roles
                    if role is None:
                        # inspect class name
                        role = m.__class__.__name__.lower()
                        if 'system' in role:
                            r = 'system'
                        else:
                            r = 'user'
                    else:
                        r = role
                    content = getattr(m, 'content', str(m))
                except Exception:
                    r = 'user'
                    content = str(m)
                payload.append({"role": r if r in ("system", "user", "assistant") else "user", "content": content})

            resp = openai.ChatCompletion.create(model=self.model, messages=payload, temperature=self.temperature)
            text = resp['choices'][0]['message']['content']

            class Response:
                def __init__(self, content):
                    self.content = content

            return Response(text)
try:
    from langchain.schema import HumanMessage, SystemMessage
except Exception:
    # Minimal fallbacks used only to hold a `content` attribute when
    # the langchain package/schema is not installed or has a different layout.
    class HumanMessage:
        def __init__(self, content: str):
            self.content = content

    class SystemMessage:
        def __init__(self, content: str):
            self.content = content
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
        # Try to initialize the requested model, but fall back to known-good
        # models if the provider returns a model-not-found or access error.
        tried_models = []
        fallback_models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
        models_to_try = [self.model] + [m for m in fallback_models if m != self.model]

        last_exc = None
        for m in models_to_try:
            tried_models.append(m)
            try:
                llm = ChatOpenAI(
                    model=m,
                    temperature=0.3,
                    api_key=self.api_key,
                    max_retries=3
                )
                app_logger.info(f"LLM service initialized with model: {m}")
                # remember which model actually worked
                self.model = m
                return llm
            except Exception as e:
                # Keep trying other fallback models when possible.
                app_logger.warning(f"Failed to initialize ChatOpenAI with model '{m}': {e}")
                last_exc = e

        # If we reach here, none of the models worked.
        app_logger.error(
            f"Error initializing LLM with tried models {tried_models}: {last_exc}"
        )
        # Raise the last exception so callers can handle it.
        raise last_exc
    
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