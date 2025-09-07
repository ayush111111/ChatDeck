import datetime
import os

from dotenv import load_dotenv
from notion_client import Client

load_dotenv()
# Replace these with your actual secrets or use environment variables
NOTION_TOKEN = os.getenv("NOTION_INTERNAL_API_KEY")  # Internal integration token
NOTION_PAGE_ID = os.getenv(
    "NOTION_PAGE_ID"
)  # The ID of the page you've shared with the integration

notion = Client(auth=NOTION_TOKEN)


def get_flashcard_db_id(parent_page_id):
    """Check if the flashcard database exists and return its ID."""
    search_results = notion.search(query="Flashcards")
    for r in search_results["results"]:
        if r["object"] == "database" and r["parent"]["page_id"] == parent_page_id:
            return r["id"]
    return None


def create_flashcard_database(parent_page_id):
    """Create a new flashcard (notion) database if it doesn't exist."""
    db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "Flashcards"}}],
        properties={
            "Question": {"title": {}},
            "Answer": {"rich_text": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Learning", "color": "blue"},
                        {"name": "Reviewing", "color": "yellow"},
                        {"name": "Mastered", "color": "green"},
                    ]
                }
            },
            "Next Review": {"date": {}},
            "Topic": {"multi_select": {}},
        },
    )
    return db["id"]


def add_flashcard(db_id, question, answer, topic=None):
    notion.pages.create(
        parent={"database_id": db_id},
        properties={
            "Question": {"title": [{"text": {"content": question}}]},
            "Answer": {"rich_text": [{"text": {"content": answer}}]},
            "Status": {"select": {"name": "Learning"}},
            "Next Review": {"date": {"start": "2025-08-13"}},
            "Topic": (
                {"multi_select": [{"name": topic}]} if topic else {"multi_select": []}
            ),
        },
    )


def update_review_date(page_id, status):
    today = datetime.date.today()

    # simple Leitner intervals (in days)
    intervals = {"Learning": 1, "Reviewing": 3, "Mastered": 7}

    next_date = today + datetime.timedelta(days=intervals[status])

    notion.pages.update(
        page_id,
        properties={
            "Next Review": {"date": {"start": str(next_date)}},
            "Status": {"select": {"name": status}},
        },
    )


def handle_new_flashcard(parent_page_id, question, answer, topic=None):
    db_id = get_flashcard_db_id(parent_page_id)
    if not db_id:
        db_id = create_flashcard_database(parent_page_id)
    add_flashcard(db_id, question, answer, topic)


# Example Usage
if __name__ == "__main__":
    parent_page_id = os.getenv("NOTION_PAGE_ID")  # Replace with your actual page ID
    question = "What is the capital of France?"
    answer = "Paris"
    topic = "Geography"

    handle_new_flashcard(parent_page_id, question, answer, topic)
    print("Flashcard added successfully!")
