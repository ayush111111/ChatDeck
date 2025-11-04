import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from fcg.config.container import ServiceContainer
from fcg.config.settings import Settings
from fcg.interfaces.export_service import ExportService
from fcg.interfaces.flashcard_generator_service import FlashcardGeneratorService
from fcg.interfaces.flashcard_repository import FlashcardRepository
from fcg.repositories.notion_repository import NotionFlashcardRepository
from fcg.routes.flashcard_api import router as flashcard_router
from fcg.routes.flashcard_generation import router as generation_router
from fcg.schemas import FlashcardRequest, FlashcardResponse, TextFlashcardRequest
from fcg.services.anki_export_service import AnkiExportService
from fcg.services.database import db_service
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

    # Create FastAPI app with organized tags
    app = FastAPI(
        title="Flashcard Generator API",
        description="""
        Generate flashcards from conversations and text, with database storage and sync capabilities.

        **Current Architecture**: Chrome Extension → FastAPI → Database → Custom Anki Addon (pull-based sync)

        **Recommended Endpoints**: Use the "Flashcards API (Database)" section for all new integrations.
        """,
        version="2.0.0",
        openapi_tags=[
            {
                "name": "Flashcards API (Database)",
                "description": "✅ **Recommended**: Database-first CRUD operations for flashcards. Use these endpoints for the new architecture.",
            },
            {
                "name": "Flashcard Generation (LLM)",
                "description": "✅ **Recommended**: LLM-powered flashcard generation using OpenRouter API.",
            },
            {
                "name": "Health",
                "description": "Service health and status checks.",
            },
            {
                "name": "Deprecated",
                "description": "⚠️ **Deprecated**: Legacy endpoints that will be removed. Use the Database API instead.",
            },
        ],
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
    app.include_router(generation_router)

    # Mount static files
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app


# Create app instance
app = create_app()


@app.post(
    "/flashcards",
    response_model=FlashcardResponse,
    tags=["Deprecated"],
    deprecated=True,
    summary="[DEPRECATED] Generate flashcards (old endpoint)",
)
async def create_flashcards(request: FlashcardRequest) -> FlashcardResponse:
    """⚠️ **DEPRECATED**: This endpoint is deprecated and will be removed in a future version.

    Use the new database API endpoints instead:
    - `POST /api/v1/flashcards/generate` for LLM-based generation
    - `POST /api/v1/flashcards/batch` for batch creation

    This endpoint directly integrates with Anki/Notion which is no longer the recommended approach.
    The new architecture uses a database-first approach with pull-based sync from the Anki addon.
    """
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


@app.post(
    "/flashcards/from-text",
    response_model=FlashcardResponse,
    tags=["Deprecated"],
    deprecated=True,
    summary="[DEPRECATED] Generate flashcards from text (old endpoint)",
)
async def create_flashcards_from_text(request: TextFlashcardRequest) -> FlashcardResponse:
    """⚠️ **DEPRECATED**: This endpoint is deprecated and will be removed in a future version.

    Use the new database API endpoints instead:
    - `POST /api/v1/flashcards/generate` for LLM-based text generation
    - `POST /api/v1/flashcards/batch` for batch creation

    This endpoint directly integrates with Anki/Notion which is no longer the recommended approach.
    The new architecture uses a database-first approach with pull-based sync from the Anki addon.
    """
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


@app.get("/config", tags=["Config"])
async def get_config():
    """Get client configuration (API base URL for extensions)"""
    settings = Settings()
    return {"api_base_url": settings.api_base_url}


@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the API service is healthy and running"""
    return {"status": "healthy", "service": "flashcard-generator", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn

    settings = Settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
