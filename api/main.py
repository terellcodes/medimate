from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os

from config.settings import get_settings, Settings
from utils.constants import ResponseMessage, StatusCode
from routes.upload import router as upload_router
from routes.analysis import router as analysis_router
from services.pdf_service import pdf_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    print("Starting up...")
    
    # Initialize FDA guidelines on startup
    guidelines_path = os.path.join(os.path.dirname(__file__), "../notebooks/data/510K - Evaluating Substantial Equivalence.pdf")
    guidelines_path = os.path.abspath(guidelines_path)
    
    if os.path.exists(guidelines_path):
        try:
            success = await pdf_service.initialize_fda_guidelines(guidelines_path)
            if success:
                print("FDA guidelines loaded successfully")
            else:
                print("Failed to load FDA guidelines")
        except Exception as e:
            print(f"Error loading FDA guidelines: {str(e)}")
    else:
        print(f"FDA guidelines not found at: {guidelines_path}")
        print("API will start without FDA guidelines preloaded")
    
    yield
    # Shutdown
    print("Shutting down...")


def create_application() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        root_path="/api" if not settings.DEBUG else ""  # Add root_path for production
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=settings.ALLOW_CREDENTIALS,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )
    
    # Include routers
    app.include_router(upload_router)
    app.include_router(analysis_router)

    return app


app = create_application()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": ResponseMessage.SUCCESS,
        "code": StatusCode.HTTP_200_OK,
        "message": "API is healthy"
    }


@app.get("/api/info")
async def get_api_info(settings: Settings = Depends(get_settings)):
    """Example endpoint using settings"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "debug_mode": settings.DEBUG
    }

# Handler for Vercel serverless
handler = Mangum(app)
