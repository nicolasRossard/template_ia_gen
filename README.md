# Template for LLM Integration (IA Gen)

This template provides a foundation for quickly creating Proof of Concepts (PoCs) that require integration with Large Language Models (LLMs). It includes a complete implementation of a PDF summarizer as an example use case, showcasing how to properly structure applications that leverage LLM capabilities.

## Purpose

This template allows you to:
- Quickly prototype AI-powered applications with proper architecture
- Integrate with various LLM providers (Ollama locally or OpenAI)
- Follow software engineering best practices (MVC pattern, Hexagonal Architecture)
- Build both CLI and API interfaces for your AI applications

## Architecture

This project follows a clean **Model-View-Controller (MVC)** pattern with elements of **Hexagonal Architecture** (Ports & Adapters):

- **Model** (`app/src/model/`): 
  - Contains all business logic, domain objects, and integration with external services
  - Uses ports (interfaces) and adapters to abstract LLM provider implementations
  - Follows dependency inversion principle for flexible and testable code
  
- **View** (`app/src/view/`): 
  - Provides user interfaces (console CLI and FastAPI REST API)
  - Handles data presentation and user input
  
- **Controller** (`app/src/controller/`): 
  - Orchestrates workflow between model and view
  - Manages the application flow

## Example Use Case: PDF Summarizer

The template includes a complete implementation of a PDF summarizer that:

1. **Extracts text** from PDF documents using PyPDF2
2. **Processes the text** with a Large Language Model through a provider-agnostic interface
3. **Returns a concise summary** of the document content

### Key Components

- **PDF Extraction**: Clean extraction of text content from PDF documents
- **LLM Provider Abstraction**: Use different LLM providers through a common interface
  - Local models via Ollama API (llama2, mistral, etc.)
  - Cloud models via OpenAI API (GPT-3.5, GPT-4, etc.)
- **User Interfaces**: Choose between CLI or REST API
- **Docker Support**: Run everything in containers with Docker Compose
- **Logging**: Comprehensive logging system for tracing and debugging

## Project Structure

```
template_ia_gen/
│
├── app/                           # Application code
│   ├── src/                       # Source code following MVC pattern
│   │   ├── controller/            # Controllers orchestrate workflow
│   │   │   └── summarizer_controller.py 
│   │   │
│   │   ├── model/                 # Business logic and domain objects
│   │   │   ├── adapters/          # Implementations of external interfaces
│   │   │   │   ├── ollama_adapter.py  # Adapter for Ollama API
│   │   │   │   └── openai_adapter.py  # Adapter for OpenAI API
│   │   │   │
│   │   │   ├── domain/            # Core business logic
│   │   │   │   ├── pdf_extractor.py   # PDF text extraction
│   │   │   │   └── pdf_summarizer.py  # PDF summarization service
│   │   │   │
│   │   │   └── ports/             # Interface definitions
│   │   │       └── llm_port.py    # Abstract interface for LLM providers
│   │   │
│   │   └── view/                  # User interfaces
│   │       ├── console_view.py    # Command-line interface
│   │       └── fastapi_app.py     # REST API with FastAPI
│   │
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Configuration
│   └── Dockerfile                 # Container definition
│
├── pdfs/                          # Directory for PDF files
├── prompts/                       # Directory for prompt templates
├── docker-compose.yml             # Docker Compose configuration
├── ollama_entrypoint.sh           # Script for Ollama initialization
├── pyproject.toml                 # Project dependencies and configuration
└── README.md                      # This file
```

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/nicolasRossard/template_ia_gen.git
cd template_ia_gen
```

### 2. Install Dependencies
```bash
# Using pip
pip install -e .

# Or using uv (faster)
uv pip install -e .

# For development dependencies
uv pip install -e ".[dev]"
```

### 3. Running with Docker (Recommended)
This approach automatically sets up Ollama with the required models.

```bash
# Start the services
docker-compose up -d

# The API will be available at http://localhost:8000
```

### 4. Running Locally
If you prefer to run the application without Docker:

```bash
# Make sure you have Ollama running locally or set OPENAI_API_KEY
# For console mode
python -m app.main --mode console

# For API mode
python -m app.main --mode api --host 0.0.0.0 --port 8000
```

## Usage

### Console Mode
Interact with the application through the command line:

```bash
python -m app.main --mode console
```

Follow the prompts to:
1. Enter the path to your PDF file
2. Select the LLM provider (Ollama or OpenAI)
3. Choose the model and parameters
4. Get your summary

### API Mode
Use the REST API for programmatic access:

```bash
python -m app.main --mode api --host 0.0.0.0 --port 8000
```

#### API Endpoints

- `GET /` - API information and health check
- `POST /summarize` - Submit a PDF for summarization

Example request to `/summarize`:

```json
{
  "pdf_path": "/path/to/document.pdf",
  "provider": "ollama",
  "model": "llama2",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

## Development

### Project Requirements
- Python 3.12+ (recommended)
- Docker and Docker Compose (for containerized setup)
- For Ollama: Local Ollama instance (included in Docker setup)
- For OpenAI: Valid API key

### Development Dependencies
Install the development dependencies for linting, testing, and formatting:

```bash
uv pip install -e ".[dev]"
```

### Creating Your Own Use Cases

To create a new LLM-powered application using this template:

1. Create new domain objects in `app/src/model/domain/`
2. Define new ports if needed in `app/src/model/ports/`
3. Create controllers for your workflows in `app/src/controller/`
4. Add views as needed in `app/src/view/`

The existing PDF summarizer serves as a reference implementation that demonstrates:
- How to structure domain logic
- How to abstract external services
- How to create value objects with Pydantic
- How to implement proper logging and error handling

## Architecture Guidelines

This template encourages:

1. **Separation of Concerns**: Clear boundaries between model, view, and controller
2. **Dependency Inversion**: High-level modules don't depend on low-level modules
3. **Interface Segregation**: Small, focused interfaces for each service
4. **Immutable Value Objects**: Using Pydantic with frozen config for data transfer
5. **Proper Logging**: Consistent logging patterns throughout the application

## License

MIT

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.
