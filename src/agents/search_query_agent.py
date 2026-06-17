import os
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv


load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "file-index"


class SearchQueryAgent:
    def __init__(self, index_name: str = INDEX_NAME):
        if not SEARCH_ENDPOINT or not SEARCH_KEY:
            raise ValueError("AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_KEY is missing")

        self.index_name = index_name
        self.search_client = SearchClient(
            endpoint=SEARCH_ENDPOINT,
            index_name=index_name,
            credential=AzureKeyCredential(SEARCH_KEY),
        )

    def query(self, question: str, top: int = 5) -> list[dict[str, Any]]:
        if not question.strip():
            return []

        results = self.search_client.search(
            search_text=question,
            top=top,
            select=["id", "content", "file_name", "index"],
        )

        documents = []
        for result in results:
            documents.append(
                {
                    "id": result.get("id"),
                    "file_name": result.get("file_name"),
                    "content": result.get("content"),
                    "index": result.get("index"),
                    "score": result.get("@search.score"),
                }
            )

        return documents
