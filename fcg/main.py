from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fcg.models import FlashcardRequest, FlashcardResponse
from fcg.config.settings import Settings
from fcg.config.container import ServiceContainer
from fcg.use_cases.flashcard_use_case import FlashcardUseCase
from fcg.interfaces.flashcard_generator_service import FlashcardGeneratorService
from fcg.interfaces.flashcard_repository import FlashcardRepository
from fcg.interfaces.export_service import ExportService
from fcg.services.openrouter_flashcard_service import OpenRouterFlashcardService
from fcg.repositories.notion_repository import NotionFlashcardRepository
from fcg.services.anki_export_service import AnkiExportService


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    # Load settings
    settings = Settings()

    # Create service container
    container = ServiceContainer(settings)

    # Register services
    container.register_factory(
        FlashcardGeneratorService, lambda s: OpenRouterFlashcardService(s)
    )
    container.register_factory(
        FlashcardRepository, lambda s: NotionFlashcardRepository(s)
    )
    container.register_factory(ExportService, lambda s: AnkiExportService())

    # Create FastAPI app
    app = FastAPI(
        title="Flashcard Generator API",
        description="Generate flashcards from conversations and export to various formats",
        version="1.0.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type"],
        max_age=600,
    )

    # Store container in app state
    app.state.container = container

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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "flashcard-generator"}


if __name__ == "__main__":
    import uvicorn

    settings = Settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
