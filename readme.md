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


I am the user for it - I frequently need to summarise books into anki cards
- varying number of cards
- density of information
- type of card - quiz / fill in the blank / thorough (dense)
- wasnt the "core" purpose summarising chats though - i use it more for books than chats

- to summarise files, the app will need a frontend or a sidebar to upload files

Priority

- anki connection - syncing without desktop app is not possible - try with the app
- book to flashcard - algorithm and logic - will need time and iterations
- - v1 - the design pattern book (410 pages - try set of algorithms, images, core "22" patterns + solid + oop = ~30 "concepts" - 2-3 flashcards per pattern and 1 for for the rest = ~70 cards)
    - density of information
    - "golden" card set from anki

there are better interfaces out there - so just focus on getting the algorithm right for you
