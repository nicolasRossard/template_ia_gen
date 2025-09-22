"""
LLM Port - Interface for different LLM providers.
"""
from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class LLMRequest(BaseModel):
    """
    Value Object for a LLM request.
    Immutable object representing a prompt to be sent to an LLM.
    """
    model_config = ConfigDict(frozen=True)
    
    prompt: str = Field(..., description="The prompt text to be sent to the LLM.")
    model: str = Field(..., description="The model to use for the LLM request.")
    temperature: float = Field(0.7, description="Controls randomness in the response. Higher values (e.g., 0.8) make output more random, lower values (e.g., 0.2) make it more deterministic.")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate in the response.")


class LLMResponse(BaseModel):
    """
    Value Object for a LLM response.
    Immutable object representing a response from an LLM.
    """
    model_config = ConfigDict(frozen=True)
    
    text: str = Field(..., description="The generated text response from the LLM.")
    model: str = Field(..., description="The model that was used to generate the response.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata from the LLM response.")


class LLMPort(ABC):
    """
    Abstract interface for LLM providers.
    All concrete LLM implementations must inherit from this class.
    """
    
    def __init__(self):
        """Initialize the LLM interface with a logger."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from the LLM based on the provided request.
        
        Args:
            request (LLMRequest): The request containing the prompt and parameters.
            
        Returns:
            LLMResponse: The response from the LLM.
        """
        pass