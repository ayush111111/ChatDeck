Build both export paths into your app:

POST /add_card → always saves to DB

POST /send_to_notion → for Notion integration (easy + automatic)

GET /anki_deck → for .apkg download (Anki users)


Current status - extension sends an empty message to the backend api
TODO 
- send correct content - currently, the button is triggered after the use selects some content and passes it to the backend - should the entire page be selected?
- analyse content and create the flashcard content - done
    - LLM call
        - scaffolding should be compatible with ollama (openai spec should be fine) - done via openrouter
        - using openrouter - cheapest available LLM
            - what input parameters are expected by the template, the LLM should provide these as output - find the hn article either in notes  - question, answer, id - for nwo

- send flashcard to a users platform
    - notion page - https://www.notion.com/templates/flashcards
        - need a secure mechanism to do this for the user
    - anki card

add a cap to the conversation / find a way to deal with large conversations
add a message "creating flashcard, which changes to added flashcard"
