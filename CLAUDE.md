# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

MediMate is a full-stack application with separate API and frontend services:

### API (FastAPI Backend)
- **Location**: `api/` directory
- **Framework**: FastAPI with Pydantic for data validation
- **Structure**: Domain-driven design with clear separation of concerns
  - `config/`: Application settings and configuration management
  - `models/`: Data models (domain, schemas, database)
  - `services/`: Business logic layer
  - `core/`: Core application functionality
  - `utils/`: Utility functions and constants
- **Dependencies**: Managed via `pyproject.toml` with optional dev dependencies
- **Deployment**: Configured for Vercel serverless with Mangum adapter

### Frontend (Next.js)
- **Location**: `frontend/` directory  
- **Framework**: Next.js 15 with React 19, TypeScript, and Tailwind CSS
- **Structure**: App Router architecture
- **Build**: Uses Turbopack for development

### Notebooks
- **Location**: `notebooks/` directory
- **Purpose**: Research and prototyping with Jupyter notebooks
- **Data**: Contains 510K regulatory documents for analysis

## Development Commands

### API Development
```bash
# Navigate to API directory
cd api

# Install dependencies (including dev tools)
uv sync

# Run development server
uvicorn main:app --reload

# Development tools
black .              # Format code
isort .              # Sort imports  
flake8 .             # Lint code
mypy .               # Type checking
pytest               # Run tests
pytest --cov=app     # Run tests with coverage

# Run all checks
black . && isort . && flake8 . && mypy . && pytest
```

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Development server with Turbopack
npm run dev

# Build and lint
npm run build
npm run lint
```

### Environment Setup
- API uses `.env` file in `api/` directory
- Settings managed through `config/settings.py` with Pydantic BaseSettings
- CORS configured for local development and Vercel deployments

## Key Configuration Files

- `api/pyproject.toml`: Python dependencies and project metadata
- `api/config/settings.py`: Environment-based configuration with CORS settings
- `frontend/package.json`: Node.js dependencies and scripts
- `api/main.py`: FastAPI application factory with CORS middleware
- `api/vercel.json`: Vercel deployment configuration
- `frontend/next.config.ts`: Next.js configuration

## Testing

- API: pytest with async support (`pytest-asyncio`)
- Test files follow `test_*.py` naming convention
- Organized in `tests/unit/`, `tests/integration/`, and `tests/fixtures/`