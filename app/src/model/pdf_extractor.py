"""
PDF Extractor - Functionality for extracting text from PDF documents.
"""
import logging
import os
from typing import List, Optional

import PyPDF2
from pydantic import BaseModel, Field, ConfigDict


class PDFExtractorConfig(BaseModel):
    """
    Configuration for the PDF extractor.
    """
    extract_images: bool = Field(False, description="Whether to extract images from the PDF.")
    extract_tables: bool = Field(False, description="Whether to extract tables from the PDF.")
    page_range: Optional[tuple[int, int]] = Field(None, description="Page range to extract (start_page, end_page). None means all pages.")


class PDFExtractResult(BaseModel):
    """
    Value Object for PDF extraction results.
    Immutable object representing the text extracted from a PDF.
    """
    model_config = ConfigDict(frozen=True)
    
    text: str = Field(..., description="The extracted text content.")
    path: str = Field(..., description="The path to the PDF file.")
    pages: int = Field(..., description="The number of pages in the PDF.")
    metadata: dict = Field(default_factory=dict, description="PDF metadata like author, title, etc.")


class PDFExtractor:
    """
    Extracts text content from PDF files using PyPDF2.
    """
    
    def __init__(self, config: Optional[PDFExtractorConfig] = None):
        """
        Initialize the PDF extractor.
        
        Args:
            config (Optional[PDFExtractorConfig]): Configuration for the PDF extractor.
                If None, default configuration will be used.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config or PDFExtractorConfig()
        self.logger.info("__init__ :: Initialized PDFExtractor")
    
    def extract(self, pdf_path: str) -> PDFExtractResult:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            PDFExtractResult: The extracted text and metadata.
            
        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the file is not a valid PDF.
        """
        self.logger.info("extract :: Extracting text from PDF: %s", pdf_path)
        
        # Check if file exists
        if not os.path.isfile(pdf_path):
            self.logger.error("extract :: PDF file not found: %s", pdf_path)
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                # Create PDF reader object
                reader = PyPDF2.PdfReader(file)
                
                # Get number of pages
                num_pages = len(reader.pages)
                self.logger.debug("extract :: PDF has %d pages", num_pages)
                
                # Extract metadata
                metadata = {}
                if reader.metadata:
                    for key, value in reader.metadata.items():
                        if key.startswith('/'):
                            key = key[1:]
                        metadata[key] = str(value)
                
                # Determine page range
                start_page = 0
                end_page = num_pages
                
                if self.config.page_range:
                    start_page = max(0, self.config.page_range[0])
                    end_page = min(num_pages, self.config.page_range[1])
                
                # Extract text from each page
                text_content = []
                for page_num in range(start_page, end_page):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    text_content.append(text)
                
                # Join all text
                full_text = "\n\n".join(text_content)
                
                self.logger.debug("extract :: Extracted %d characters of text", len(full_text))
                
                return PDFExtractResult(
                    text=full_text,
                    path=pdf_path,
                    pages=num_pages,
                    metadata=metadata
                )
                
        except PyPDF2.errors.PdfReadError as e:
            self.logger.error("extract :: Invalid PDF file: %s", str(e))
            raise ValueError(f"Invalid PDF file: {str(e)}")
        except Exception as e:
            self.logger.error("extract :: Error extracting PDF: %s", str(e))
            raise