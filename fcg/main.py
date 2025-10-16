import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from fcg.config.container import ServiceContainer
from fcg.config.settings import Settings
from fcg.services.database import db_service
from fcg.routes.flashcard_api import router as flashcard_router
from fcg.interfaces.export_service import ExportService
from fcg.interfaces.flashcard_generator_service import FlashcardGeneratorService
from fcg.interfaces.flashcard_repository import FlashcardRepository
# Import from the direct models.py file to avoid circular imports
import sys
sys.path.insert(0, os.path.dirname(__file__))
from models import FlashcardRequest, FlashcardResponse, TextFlashcardRequest
from fcg.repositories.notion_repository import NotionFlashcardRepository
from fcg.services.anki_export_service import AnkiExportService
from fcg.services.openrouter_flashcard_service import OpenRouterFlashcardService
from fcg.use_cases.flashcard_use_case import FlashcardUseCase


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    # Load settings
    settings = Settings()

    # Create service container
    container = ServiceContainer(settings)

    # Register services
    container.register_factory(FlashcardGeneratorService, lambda s: OpenRouterFlashcardService(s))
    container.register_factory(FlashcardRepository, lambda s: NotionFlashcardRepository(s))
    container.register_factory(ExportService, lambda s: AnkiExportService())

    # Initialize database
    db_service.init_database()

    # Create FastAPI app
    app = FastAPI(
        title="Flashcard Generator API",
        description="Generate flashcards from conversations and export to various formats",
        version="1.0.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for browser extension compatibility
        allow_credentials=False,  # Set to False when using allow_origins=["*"]
        allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        allow_headers=["*"],  # Allow all headers
        expose_headers=["Content-Type"],
        max_age=600,
    )

    # Store container in app state
    app.state.container = container

    # Include API routes
    app.include_router(flashcard_router)

    # Mount static files
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app


# Create app instance
app = create_app()


@app.post("/flashcards", response_model=FlashcardResponse)
async def create_flashcards(request: FlashcardRequest) -> FlashcardResponse:
    """Generate and save/export flashcards based on the request"""
    try:
        # Get use case from container
        use_case = FlashcardUseCase(app.state.container)

        # Process the request
        response = await use_case.generate_and_save_flashcards(request)

        # Return appropriate HTTP status
        if response.status == "error":
            raise HTTPException(status_code=400, detail=response.message)

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/flashcards/from-text", response_model=FlashcardResponse)
async def create_flashcards_from_text(request: TextFlashcardRequest) -> FlashcardResponse:
    """Generate and save/export flashcards from text input"""
    try:
        # Get use case from container
        use_case = FlashcardUseCase(app.state.container)

        # Process the text request
        response = await use_case.generate_flashcards_from_text(request)

        # Return appropriate HTTP status
        if response.status == "error":
            raise HTTPException(status_code=400, detail=response.message)

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "flashcard-generator"}


if __name__ == "__main__":
    import uvicorn

    settings = Settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
