"""
Console View - User interface for interacting with the application through console.
"""
import logging
import os
from typing import Optional, Dict, Any, Tuple

from pydantic import BaseModel, Field

from src.model.domain.pdf_summarizer import SummaryRequest


class ConsoleView:
    """
    Console interface for interacting with the PDF summarizer.
    """
    
    def __init__(self):
        """Initialize the console view."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("__init__ :: Initialized ConsoleView")
    
    def display_welcome(self):
        """Display welcome message and instructions."""
        print("=" * 80)
        print("PDF SUMMARIZER")
        print("=" * 80)
        print("This application summarizes PDF documents using LLM technology.")
        print("You will be prompted to provide a PDF path and choose an LLM provider.")
        print("=" * 80)
    
    def display_summary(self, summary: str, metadata: Dict[str, Any]):
        """
        Display the generated summary and metadata.
        
        Args:
            summary (str): The generated summary.
            metadata (Dict[str, Any]): Additional metadata.
        """
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(summary)
        print("\n" + "=" * 80)
        print("METADATA")
        print("=" * 80)
        
        if 'pdf_pages' in metadata:
            print(f"PDF Pages: {metadata['pdf_pages']}")
        
        if 'pdf_metadata' in metadata:
            print("PDF Metadata:")
            for key, value in metadata['pdf_metadata'].items():
                print(f"  {key}: {value}")
        
        if 'llm_metadata' in metadata:
            print("LLM Metadata:")
            for key, value in metadata['llm_metadata'].items():
                print(f"  {key}: {value}")
        
        print("=" * 80)
    
    def display_error(self, error_message: str):
        """
        Display an error message.
        
        Args:
            error_message (str): The error message to display.
        """
        print("\n" + "!" * 80)
        print("ERROR")
        print("!" * 80)
        print(error_message)
        print("!" * 80)
    
    def get_pdf_path(self) -> str:
        """
        Get the PDF path from the user.
        
        Returns:
            str: The path to the PDF file.
            
        Raises:
            ValueError: If the path is invalid.
        """
        while True:
            pdf_path = input("Enter the path to the PDF file: ").strip()
            
            if not pdf_path:
                print("Path cannot be empty. Please try again.")
                continue
            
            # Convert to absolute path if relative
            if not os.path.isabs(pdf_path):
                pdf_path = os.path.abspath(pdf_path)
            
            # Check if file exists
            if not os.path.isfile(pdf_path):
                print(f"File not found: {pdf_path}")
                print("Please enter a valid path to a PDF file.")
                continue
            
            # Check if file is a PDF
            if not pdf_path.lower().endswith('.pdf'):
                print(f"File is not a PDF: {pdf_path}")
                print("Please enter a path to a PDF file.")
                continue
            
            self.logger.debug("get_pdf_path :: Selected PDF path: %s", pdf_path)
            return pdf_path
    
    def get_provider_details(self) -> Tuple[str, str, Optional[str]]:
        """
        Get the provider, model, and API key (if needed) from the user.
        
        Returns:
            Tuple[str, str, Optional[str]]: The provider, model, and API key (if needed).
        """
        # Get provider
        while True:
            provider = input("Select LLM provider (ollama/openai): ").strip().lower()
            
            if provider not in ['ollama', 'openai']:
                print("Invalid provider. Please enter 'ollama' or 'openai'.")
                continue
            
            break
        
        # Get model
        if provider == 'ollama':
            print("Available Ollama models: llama2, mistral, gemma, etc.")
            model = input("Enter model name (default: llama2): ").strip() or "llama2"
            api_key = None
        else:  # OpenAI
            print("Available OpenAI models: gpt-3.5-turbo, gpt-4, etc.")
            model = input("Enter model name (default: gpt-3.5-turbo): ").strip() or "gpt-3.5-turbo"
            api_key = input("Enter your OpenAI API key: ").strip()
            
            if not api_key:
                print("API key is required for OpenAI. Please try again.")
                api_key = input("Enter your OpenAI API key: ").strip()
        
        self.logger.debug("get_provider_details :: Selected provider: %s, model: %s", 
                          provider, model)
        return provider, model, api_key
    
    def get_summary_request(self) -> SummaryRequest:
        """
        Get all the necessary information to create a summary request.
        
        Returns:
            SummaryRequest: The summary request.
        """
        pdf_path = self.get_pdf_path()
        provider, model, api_key = self.get_provider_details()
        
        return SummaryRequest(
            pdf_path=pdf_path,
            provider=provider,
            model=model,
            temperature=0.7,  # Default value
            openai_api_key=api_key
        )