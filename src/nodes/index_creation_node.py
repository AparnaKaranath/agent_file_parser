import os
from dotenv import load_dotenv
from src.state.agent_state import AgentState
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField
)

# Load env
load_dotenv()

# ENV variables
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "file-index"

# -------- NODE 2: CREATE INDEX -----
def create_index(state: AgentState):
    if not SEARCH_ENDPOINT or not SEARCH_KEY:
        raise ValueError("AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_KEY is missing")

    index_client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    try:
        index_client.get_index(INDEX_NAME)
        print(f"Index '{INDEX_NAME}' already exists. Skipping creation.")
        return {"index_created": True, "index_status": "exists"}
    except ResourceNotFoundError:
        print(f"Index '{INDEX_NAME}' does not exist. Creating it now.")

    fields = [
        SimpleField(name="id", type="Edm.String", key=True),
        SearchableField(name="content", type="Edm.String"),
        SimpleField(name="file_name", type="Edm.String", filterable=True),
        SimpleField(name="index", type="Edm.Int32", filterable=True)
    ]

    index = SearchIndex(name=INDEX_NAME, fields=fields)

    try:
        index_client.create_index(index)
        print(f"Index '{INDEX_NAME}' created successfully")
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        raise

    return {"index_created": True, "index_status": "created"}