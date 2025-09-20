"""
OpenAI Adapter - Implementation of LLM Port for OpenAI API.
"""
import logging
import os
from typing import Dict, Any, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.src.model.ports.llm_port import LLMPort, LLMRequest, LLMResponse


class OpenAIConfig(BaseModel):
    """
    Configuration for the OpenAI API.
    """
    api_key: str = Field(os.getenv("OPENAI_API_KEY", ""), 
                         description="API key for the OpenAI API.")
    organization: Optional[str] = Field(os.getenv("OPENAI_ORGANIZATION", None), 
                                        description="Organization ID for the OpenAI API.")
    timeout: float = Field(float(os.getenv("OPENAI_TIMEOUT", "60.0")), 
                           description="Timeout in seconds for API requests.")


class OpenAIAdapter(LLMPort):
    """
    Adapter for the OpenAI API implementing the LLMPort interface.
    """
    
    def __init__(self, config: Optional[OpenAIConfig] = None):
        """
        Initialize the OpenAI adapter.
        
        Args:
            config (OpenAIConfig): Configuration for the OpenAI API.
        """
        super().__init__()
        self.config = config or OpenAIConfig()
        
        if not self.config.api_key:
            self.logger.error("__init__ :: OpenAI API key is not set")
            raise ValueError("OpenAI API key is required. Set it via OPENAI_API_KEY environment variable.")
        
        self.client = AsyncOpenAI(
            api_key=self.config.api_key,
            organization=self.config.organization,
            timeout=self.config.timeout
        )
        self.logger.info("__init__ :: Initialized OpenAIAdapter")
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from OpenAI based on the provided request.
        
        Args:
            request (LLMRequest): The request containing the prompt and parameters.
            
        Returns:
            LLMResponse: The response from OpenAI.
            
        Raises:
            ConnectionError: If there is an issue connecting to the OpenAI API.
            ValueError: If the response from OpenAI is invalid.
        """
        self.logger.info("generate :: Sending request to OpenAI with model: %s", request.model)
        
        try:
            # Create completion request
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": request.prompt}
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens or 1024,
            )
            
            self.logger.debug("generate :: Received response from OpenAI")
            
            # Extract the response text
            if not response.choices or len(response.choices) == 0:
                raise ValueError("No choices in OpenAI response")
            
            text = response.choices[0].message.content or ""
            
            # Build metadata
            metadata = {
                "model_name": response.model,
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
                "finish_reason": response.choices[0].finish_reason if response.choices else None,
            }
            
            return LLMResponse(
                text=text,
                model=request.model,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error("generate :: Error with OpenAI API: %s", str(e))
            raise ValueError(f"Error with OpenAI API: {str(e)}")