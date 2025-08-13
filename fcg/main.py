import json
import uuid
from typing import List

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from fcg.models import ChatMessage, FlashcardRequest
from fcg.utils.anki import generate_apkg
from fcg.utils.flashcard_generator import generate_flashcards
from fcg.utils.notion import send_to_notion
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "https://chat.openai.com",
        "https://chatgpt.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type"],
    max_age=600,
)


@app.post("/flashcards")
async def create_flashcards(request: FlashcardRequest):
    try:
        flashcards = await generate_flashcards(request.conversation)
    except Exception as e:
        return {"error": str(e)}

    # how to handle case where flashcards has an
    if request.destination == "notion":
        send_to_notion(flashcards)
        return {"status": "sent_to_notion"}
    elif request.destination == "anki":
        file_path = generate_apkg(flashcards)
        return {"status": "apkg_generated", "path": file_path}
    else:
        return {"error": "invalid destination"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
