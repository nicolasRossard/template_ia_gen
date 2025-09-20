#!/usr/bin/env python3
"""
Main entry point for the PDF Summarizer application.
"""
import argparse
import asyncio
import logging
import sys
from contextlib import asynccontextmanager

import config
from fastapi import FastAPI
from fastapi.routing import APIRoute

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.controller.summarizer_controller import SummarizerController
from src.view.fastapi_app import router as api_router


# Set up logger
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events for async startup and shutdown"""
    # === STARTUP ===
    logger.info("lifespan :: 🚀 Starting async application initialization...")

    try:
        # Initialize any resources here
        logger.info("lifespan :: ✅ Async application initialization completed successfully!")

    except Exception as e:
        logger.error(f"lifespan :: ❌ Startup failed: {str(e)}")
        raise

    # Application is ready
    yield

    # === SHUTDOWN ===
    logger.info("lifespan :: 🔄 Starting application shutdown...")
    # Add any cleanup operations here if needed
    logger.info("lifespan :: ✅ Application shutdown completed.")


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate a unique ID for OpenAPI documentation."""
    # Ensure route.tags is not empty and route.name is defined
    if route.tags and route.name:
        return f"{route.tags[0]}-{route.name}"
    # Fallback if tags or name are missing
    return route.name or f"unnamed-route-{route.path_format}"


# Create the FastAPI app
app = FastAPI(
    title="PDF Summarizer API",
    description="API for summarizing PDF documents using LLM technology.",
    version="1.0.0",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

# Set up SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here",  # Replace with a proper secret key from environment variable
    max_age=1800,  # 30 minutes
    https_only=False,  # Set to True in production
    same_site="lax",
)


# Middleware to handle authentication and CORS
@app.middleware("http")
async def postprocess_middleware(request, call_next):
    """Process requests and responses for authentication and CORS."""
    response = await call_next(request)

    # Handle 401 responses
    if response.status_code == 401:
        # Ensure CORS headers are set for authentication errors
        response.headers["Access-Control-Allow-Origin"] = request.headers.get(
            "origin", "*"
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"

    return response


# Include the API router
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning basic information about the API."""
    return {
        "message": "PDF Summarizer API",
        "version": "1.0.0",
        "documentation": "/docs",
        "api_endpoints": "/api"
    }


def setup_logging(level=logging.INFO):
    """
    Set up logging configuration.
    
    Args:
        level: The logging level to use.
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


async def run_console_mode():
    """Run the application in console mode."""
    controller = SummarizerController()
    await controller.run()


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="PDF Summarizer Application")
    parser.add_argument(
        "--mode", 
        choices=["console", "api"], 
        default="console",
        help="Run mode: 'console' for CLI interface, 'api' for REST API"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="Host to bind to when running in API mode"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to bind to when running in API mode"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    logger = logging.getLogger("main")
    logger.info("main :: Starting PDF Summarizer application in %s mode", args.mode)
    
    try:
        if args.mode == "console":
            # Run in console mode
            asyncio.run(run_console_mode())
        else:
            # Run in API mode
            logger.info("main :: Starting API server on %s:%s", args.host, args.port)
            import uvicorn
            uvicorn.run("app.main:app", host=args.host, port=args.port, reload=True)
    except KeyboardInterrupt:
        logger.info("main :: Application stopped by user")
    except Exception as e:
        logger.error("main :: Unexpected error: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()