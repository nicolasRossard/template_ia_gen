"""
Summarizer Controller - Orchestrates the model and view for PDF summarization.
"""
import logging
import asyncio
from typing import Optional

from src.model.pdf_summarizer import PDFSummarizer, SummaryRequest, SummaryResponse
from src.view.console_view import ConsoleView


class SummarizerController:
    """
    Controller that orchestrates the model and view for PDF summarization.
    """
    
    def __init__(self):
        """Initialize the summarizer controller."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.view = ConsoleView()
        self.summarizer = PDFSummarizer()
        self.logger.info("__init__ :: Initialized SummarizerController")
    
    async def run(self):
        """
        Run the controller flow for the console interface.
        
        This method orchestrates the following steps:
        1. Display welcome message
        2. Get user input for PDF path and LLM provider
        3. Process the request using the summarizer
        4. Display the results or error message
        """
        self.logger.info("run :: Starting controller flow")
        
        try:
            # Display welcome message
            self.view.display_welcome()
            
            # Get user input
            request = self.view.get_summary_request()
            self.logger.info("run :: Received request for PDF: %s with provider: %s", 
                            request.pdf_path, request.provider)
            
            # Process the request
            self.logger.info("run :: Processing request")
            response = await self.summarizer.summarize(request)
            
            # Display the results
            self.logger.info("run :: Displaying results")
            self.view.display_summary(response.summary, response.metadata)
            
            self.logger.info("run :: Controller flow completed successfully")
            return response
            
        except Exception as e:
            self.logger.error("run :: Error in controller flow: %s", str(e))
            self.view.display_error(str(e))
            return None