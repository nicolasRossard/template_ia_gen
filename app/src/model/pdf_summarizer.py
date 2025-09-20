"""
PDF Summarizer - Combines PDF extraction and LLM to create summaries.
"""
import logging
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict

from src.model.pdf_extractor import PDFExtractor, PDFExtractorConfig, PDFExtractResult
from src.model.llm_port import LLMPort, LLMRequest, LLMResponse
from src.model.ollama_adapter import OllamaAdapter, OllamaConfig
from src.model.openai_adapter import OpenAIAdapter, OpenAIConfig


class SummaryRequest(BaseModel):
    """
    Value Object for a summary request.
    Immutable object representing a request to summarize a PDF.
    """
    model_config = ConfigDict(frozen=True)
    
    pdf_path: str = Field(..., description="Path to the PDF file to summarize.")
    provider: str = Field(..., description="LLM provider to use ('ollama' or 'openai').")
    model: str = Field(..., description="The model to use for summarization.")
    temperature: float = Field(0.7, description="Controls randomness in the response.")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate in the response.")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key (required if provider is 'openai').")


class SummaryResponse(BaseModel):
    """
    Value Object for a summary response.
    Immutable object representing a summary of a PDF.
    """
    model_config = ConfigDict(frozen=True)
    
    summary: str = Field(..., description="The generated summary text.")
    pdf_path: str = Field(..., description="Path to the PDF that was summarized.")
    provider: str = Field(..., description="LLM provider that was used.")
    model: str = Field(..., description="The model that was used.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata.")


class PDFSummarizer:
    """
    Service that combines PDF extraction and LLM processing to create summaries.
    """
    
    def __init__(self):
        """Initialize the PDF summarizer."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pdf_extractor = PDFExtractor()
        self.logger.info("__init__ :: Initialized PDFSummarizer")
    
    def _get_llm_adapter(self, request: SummaryRequest) -> LLMPort:
        """
        Get the appropriate LLM adapter based on the provider.
        
        Args:
            request (SummaryRequest): The summary request.
            
        Returns:
            LLMPort: The LLM adapter.
            
        Raises:
            ValueError: If the provider is not supported or the request is invalid.
        """
        if request.provider.lower() == 'ollama':
            return OllamaAdapter()
        elif request.provider.lower() == 'openai':
            if not request.openai_api_key:
                raise ValueError("OpenAI API key is required for OpenAI provider")
            config = OpenAIConfig(api_key=request.openai_api_key)
            return OpenAIAdapter(config)
        else:
            raise ValueError(f"Unsupported provider: {request.provider}")
    
    def _create_summary_prompt(self, pdf_result: PDFExtractResult) -> str:
        """
        Create a prompt for the LLM to generate a summary.
        
        Args:
            pdf_result (PDFExtractResult): The PDF extraction result.
            
        Returns:
            str: The prompt for the LLM.
        """
        return f"""
Please summarize the following document in a comprehensive way:

DOCUMENT TITLE: {pdf_result.metadata.get('Title', 'Unknown')}
DOCUMENT AUTHOR: {pdf_result.metadata.get('Author', 'Unknown')}
DOCUMENT PAGES: {pdf_result.pages}

DOCUMENT CONTENT:
{pdf_result.text}

Please provide a structured summary covering the main points, key findings, and important details.
"""
    
    async def summarize(self, request: SummaryRequest) -> SummaryResponse:
        """
        Summarize a PDF document using the specified LLM provider.
        
        Args:
            request (SummaryRequest): The summary request.
            
        Returns:
            SummaryResponse: The summary response.
            
        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the request is invalid or the PDF extraction fails.
            ConnectionError: If there is an issue connecting to the LLM provider.
        """
        self.logger.info("summarize :: Summarizing PDF: %s with provider: %s", 
                         request.pdf_path, request.provider)
        
        try:
            # Extract text from PDF
            pdf_result = self.pdf_extractor.extract(request.pdf_path)
            self.logger.info("summarize :: Extracted %d characters from PDF", 
                             len(pdf_result.text))
            
            # Get LLM adapter
            llm_adapter = self._get_llm_adapter(request)
            
            # Create prompt
            prompt = self._create_summary_prompt(pdf_result)
            
            # Create LLM request
            llm_request = LLMRequest(
                prompt=prompt,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # Generate summary
            self.logger.info("summarize :: Sending request to LLM")
            llm_response = await llm_adapter.generate(llm_request)
            
            # Create summary response
            return SummaryResponse(
                summary=llm_response.text,
                pdf_path=request.pdf_path,
                provider=request.provider,
                model=request.model,
                metadata={
                    "pdf_pages": pdf_result.pages,
                    "pdf_metadata": pdf_result.metadata,
                    "llm_metadata": llm_response.metadata
                }
            )
            
        except Exception as e:
            self.logger.error("summarize :: Error summarizing PDF: %s", str(e))
            raise