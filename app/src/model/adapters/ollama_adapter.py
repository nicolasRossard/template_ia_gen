"""
Ollama Adapter - Implementation of LLM Port for Ollama API.
"""
import logging
import json
import os
from typing import Dict, Any, Optional
import httpx
from pydantic import BaseModel, Field

from src.model.ports.llm_port import LLMPort, LLMRequest, LLMResponse


class OllamaConfig(BaseModel):
    """
    Configuration for the Ollama API.
    """
    base_url: str = Field(os.getenv("OLLAMA_API_URL", "http://localhost:11434"), 
                          description="Base URL for the Ollama API.")
    timeout: int = Field(int(os.getenv("OLLAMA_TIMEOUT", "60")), 
                         description="Timeout in seconds for API requests.")


class OllamaAdapter(LLMPort):
    """
    Adapter for the Ollama API implementing the LLMPort interface.
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """
        Initialize the Ollama adapter.
        
        Args:
            config (Optional[OllamaConfig]): Configuration for the Ollama API.
                If None, default configuration will be used.
        """
        super().__init__()
        self.config = config or OllamaConfig()
        self.logger.info("__init__ :: Initialized OllamaAdapter with base URL: %s", self.config.base_url)
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from Ollama based on the provided request.
        
        Args:
            request (LLMRequest): The request containing the prompt and parameters.
            
        Returns:
            LLMResponse: The response from Ollama.
            
        Raises:
            ConnectionError: If there is an issue connecting to the Ollama API.
            ValueError: If the response from Ollama is invalid.
        """
        self.logger.info("generate :: Sending request to Ollama with model: %s", request.model)
        
        api_url = f"{self.config.base_url}/api/generate"
        
        # Prepare the request payload
        payload = {
            "model": request.model,
            "prompt": request.prompt,
            "option": {
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            },
             "stream": False
        }
        
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        self.logger.debug("generate :: Request payload: %s", payload)
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    api_url,
                    json=payload
                )
                
                response.raise_for_status()
                self.logger.debug(f"generate :: Received response from Ollama {response}")

                response_json = response.json()
                self.logger.debug("generate :: Received response from Ollama")
                self.logger.debug("generate :: Response JSON: %s", response_json)
                # Extract the response text
                text = response_json.get("response", "")
                
                # Build metadata
                metadata = {
                    "model_name": response_json.get("model", request.model),
                    "total_duration": response_json.get("total_duration", 0),
                    "load_duration": response_json.get("load_duration", 0),
                    "prompt_eval_count": response_json.get("prompt_eval_count", 0),
                    "eval_count": response_json.get("eval_count", 0),
                    "eval_duration": response_json.get("eval_duration", 0),
                }
                
                return LLMResponse(
                    text=text,
                    model=request.model,
                    metadata=metadata
                )
                    
        except httpx.RequestError as e:
            self.logger.error("generate :: Connection error with Ollama API: %s", str(e))
            raise ConnectionError(f"Failed to connect to Ollama API: {str(e)}")
        except json.JSONDecodeError as e:
            self.logger.error("generate :: Invalid JSON response from Ollama API: %s", str(e))
            raise ValueError(f"Invalid response from Ollama API: {str(e)}")
        except Exception as e:
            self.logger.error("generate :: Unexpected error: %s", str(e))
            raise