"""
FastAPI App - REST API interface for the PDF summarizer application.
"""
import logging
import os
import tempfile
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel, Field

from src.model.domain.pdf_summarizer import PDFSummarizer, SummaryRequest, SummaryResponse


# API request and response models
class SummarizeParams(BaseModel):
    """
    Parameters for PDF summarization (excluding the file itself).
    """
    provider: str = Field(..., description="LLM provider to use ('ollama' or 'openai').")
    model: str = Field(..., description="The model to use for summarization.")
    temperature: float = Field(0.7, description="Controls randomness in the response.")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate.")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key (required if provider is 'openai').")


class APIResponse(BaseModel):
    """
    API response model with the summary and metadata.
    """
    summary: str = Field(..., description="The generated summary text.")
    filename: str = Field(..., description="Name of the PDF file that was summarized.")
    provider: str = Field(..., description="LLM provider that was used.")
    model: str = Field(..., description="The model that was used.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata.")


# Create the APIRouter instead of FastAPI app
router = APIRouter(
    prefix="/api",
    tags=["summarizer"]
)


# Set up logger
logger = logging.getLogger("fastapi_app")


@router.get("/", summary="Root Endpoint")
async def api_root():
    """Root endpoint returning basic information about the API."""
    return {
        "message": "PDF Summarizer API",
        "version": "1.0.0",
        "endpoints": {
            "/api/summarize": "POST - Summarize a PDF document"
        }
    }


@router.post("/summarize", response_model=APIResponse, summary="Summarize PDF")
async def summarize_pdf(
    file: UploadFile = File(...),
    provider: str = Form(...),
    model: str = Form(...),
    temperature: float = Form(0.7),
    max_tokens: Optional[int] = Form(None),
    openai_api_key: Optional[str] = Form(None)
):
    """
    Summarize a PDF document using the specified LLM provider.
    
    Args:
        file: The PDF file to summarize.
        provider: LLM provider to use ('ollama' or 'openai').
        model: The model to use for summarization.
        temperature: Controls randomness in the response.
        max_tokens: Maximum number of tokens to generate.
        openai_api_key: OpenAI API key (required if provider is 'openai').
        
    Returns:
        APIResponse: The summary response.
        
    Raises:
        HTTPException: If there is an error processing the request.
    """
    logger.info("summarize_pdf :: Received request to summarize PDF: %s", file.filename)
    
    # Check if the uploaded file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        logger.error("summarize_pdf :: Uploaded file is not a PDF: %s", file.filename)
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF")
    
    temp_path = None
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Create summary request
        summary_request = SummaryRequest(
            pdf_path=temp_path,
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Create summarizer
        summarizer = PDFSummarizer()
        
        # Generate summary
        response = await summarizer.summarize(summary_request)
        
        logger.info("summarize_pdf :: Successfully summarized PDF: %s", file.filename)
        
        # Return API response
        return APIResponse(
            summary=response.summary,
            filename=file.filename,
            provider=response.provider,
            model=response.model,
            metadata=response.metadata
        )
        
    except FileNotFoundError as e:
        logger.error("summarize_pdf :: PDF file not found: %s", str(e))
        raise HTTPException(status_code=404, detail=f"PDF file not found: {str(e)}")
    except ValueError as e:
        logger.error("summarize_pdf :: Invalid request: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except ConnectionError as e:
        logger.error("summarize_pdf :: Connection error: %s", str(e))
        raise HTTPException(status_code=503, detail=f"Connection error: {str(e)}")
    except Exception as e:
        logger.error("summarize_pdf :: Unexpected error: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Make sure to clean up the temporary file if it exists
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning("summarize_pdf :: Failed to delete temporary file: %s", str(e))

# This file is now a module providing a router, not a directly runnable app
# The main application is now defined in app/main.py