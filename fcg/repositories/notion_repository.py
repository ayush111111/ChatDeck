import datetime
from typing import Any, Dict, List, Optional

from notion_client import Client

from fcg.config.settings import Settings
from fcg.interfaces.flashcard_repository import FlashcardRepository


class NotionFlashcardRepository(FlashcardRepository):
    """Notion implementation of flashcard repository"""

    def __init__(self, settings: Settings):
        if not settings.notion_api_key:
            raise ValueError("Notion API key is required")
        if not settings.notion_page_id:
            raise ValueError("Notion page ID is required")

        self.client = Client(auth=settings.notion_api_key)
        self.page_id = settings.notion_page_id
        self._db_id_cache: Optional[str] = None

    async def save_flashcards(self, flashcards: List[Dict[str, Any]]) -> bool:
        """Save flashcards to Notion database"""
        try:
            db_id = await self._get_or_create_database()

            for card in flashcards:
                await self._create_flashcard_page(db_id, card)

            return True
        except Exception as e:
            # Log error in production
            print(f"Error saving flashcards to Notion: {e}")
            return False

    async def get_flashcards(
        self, filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve flashcards from Notion database"""
        try:
            db_id = await self._get_database_id()
            if not db_id:
                return []

            # Query the database
            query_filter = self._build_notion_filter(filters) if filters else None
            response = self.client.databases.query(
                database_id=db_id, filter=query_filter
            )

            return [
                self._convert_notion_page_to_flashcard(page)
                for page in response["results"]
            ]

        except Exception as e:
            print(f"Error retrieving flashcards from Notion: {e}")
            return []

    async def _get_or_create_database(self) -> str:
        """Get existing database ID or create new one"""
        if self._db_id_cache:
            return self._db_id_cache

        db_id = await self._get_database_id()
        if not db_id:
            db_id = await self._create_database()

        self._db_id_cache = db_id
        return db_id

    async def _get_database_id(self) -> Optional[str]:
        """Check if flashcard database exists and return its ID"""
        search_results = self.client.search(query="Flashcards")

        for result in search_results["results"]:
            if (
                result["object"] == "database"
                and "page_id" in result["parent"]
                and result["parent"]["page_id"] == self.page_id
            ):
                return result["id"]

        return None

    async def _create_database(self) -> str:
        """Create a new flashcard database"""
        database = self.client.databases.create(
            parent={"type": "page_id", "page_id": self.page_id},
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
        return database["id"]

    async def _create_flashcard_page(self, db_id: str, card: Dict[str, Any]):
        """Create a single flashcard page in Notion"""
        properties = {
            "Question": {"title": [{"text": {"content": card["question"]}}]},
            "Answer": {"rich_text": [{"text": {"content": card["answer"]}}]},
            "Status": {"select": {"name": "Learning"}},
            "Next Review": {"date": {"start": datetime.date.today().isoformat()}},
        }

        # Add topic if provided
        if topic := card.get("topic"):
            properties["Topic"] = {"multi_select": [{"name": topic}]}
        else:
            properties["Topic"] = {"multi_select": []}

        self.client.pages.create(parent={"database_id": db_id}, properties=properties)

    def _build_notion_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert generic filters to Notion-specific filter format"""
        # Implementation depends on specific filter needs
        # This is a placeholder for filter conversion logic
        return {}

    def _convert_notion_page_to_flashcard(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Notion page to standardized flashcard format"""
        properties = page["properties"]

        return {
            "id": page["id"],
            "question": self._extract_text_from_title(properties.get("Question", {})),
            "answer": self._extract_text_from_rich_text(properties.get("Answer", {})),
            "topic": self._extract_topic(properties.get("Topic", {})),
            "status": self._extract_select_value(properties.get("Status", {})),
        }

    def _extract_text_from_title(self, title_property: Dict[str, Any]) -> str:
        """Extract text from Notion title property"""
        if "title" in title_property and title_property["title"]:
            return title_property["title"][0]["text"]["content"]
        return ""

    def _extract_text_from_rich_text(self, rich_text_property: Dict[str, Any]) -> str:
        """Extract text from Notion rich text property"""
        if "rich_text" in rich_text_property and rich_text_property["rich_text"]:
            return rich_text_property["rich_text"][0]["text"]["content"]
        return ""

    def _extract_topic(self, multi_select_property: Dict[str, Any]) -> str:
        """Extract first topic from multi-select property"""
        if (
            "multi_select" in multi_select_property
            and multi_select_property["multi_select"]
        ):
            return multi_select_property["multi_select"][0]["name"]
        return ""

    def _extract_select_value(self, select_property: Dict[str, Any]) -> str:
        """Extract value from select property"""
        if "select" in select_property and select_property["select"]:
            return select_property["select"]["name"]
        return ""
