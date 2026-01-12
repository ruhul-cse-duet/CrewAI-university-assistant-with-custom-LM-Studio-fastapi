"""
Custom LLM Implementation for LM Studio
Completely replaces LangChain OpenAI dependency
"""

import requests
from typing import Any, List, Optional, Dict
import logging
from config import Config

logger = logging.getLogger(__name__)


class LMStudioLLM:
    """
    Custom LLM class that works with CrewAI
    Compatible with CrewAI's agent system
    """
    
    def __init__(self):
        self.base_url = Config.LM_STUDIO_BASE_URL
        self.model = Config.LM_STUDIO_MODEL
        self.api_key = Config.LM_STUDIO_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info(f"LMStudioLLM initialized with model: {self.model}")
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """
        Main method called by CrewAI agents
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        try:
            return self._call(prompt, **kwargs)
        except Exception as e:
            logger.error(f"Error in invoke: {str(e)}")
            raise
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """
        Internal call method with timeout handling
        
        Args:
            prompt: Input text
            stop: Stop sequences
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        try:
            # Prepare payload
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful university assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get("temperature", 0.3),
                "max_tokens": kwargs.get("max_tokens", 200),
                "stream": False
            }
            
            if stop:
                payload["stop"] = stop
            
            # Make API request with shorter timeout
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=500  # Reduced from 200 to 60 seconds
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract content
            content = result["choices"][0]["message"]["content"]
            return content.strip()
            
        except requests.exceptions.Timeout:
            logger.error("LM Studio request timeout (60s)")
            return "Error: Request timeout. The LLM is taking too long to respond. Please try again."
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to LM Studio")
            return "Error: Cannot connect to LM Studio. Please ensure it's running on port 1234."
        except Exception as e:
            logger.error(f"Error calling LM Studio: {str(e)}")
            return f"Error: {str(e)}"
    
    def call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Alias for _call for compatibility"""
        return self._call(prompt, stop=stop)
    
    def __call__(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Make class callable"""
        return self._call(prompt, stop=stop)


def get_llm():
    """Get LM Studio LLM instance"""
    return LMStudioLLM()
