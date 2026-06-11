import os
import json
from dotenv import load_dotenv
from src.state.agent_state import AgentState
from azure.core.credentials import AzureKeyCredential
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
print("INDEX CREATION &&&&&")
# -------- NODE 2: CREATE INDEX -----
def create_index(state: AgentState):
    if not SEARCH_ENDPOINT or not SEARCH_KEY:
        raise ValueError("AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_KEY is missing")
    print("Got search keysss")
    index_client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    fields = [
        SimpleField(name="id", type="Edm.String", key=True),
        SearchableField(name="content", type="Edm.String"),
        SimpleField(name="file_name", type="Edm.String", filterable=True),
        SimpleField(name="index", type="Edm.Int32", filterable=True)
    ]

    index = SearchIndex(name=INDEX_NAME, fields=fields)
    print("Index creation done.....*****")
    try:
        index_client.create_index(index)
        print(f"Index '{INDEX_NAME}' created successfully")
    except Exception as e:
        if "already exists" in str(e):
            print(f"Index '{INDEX_NAME}' already exists")
        else:
            print(f"Error creating index: {str(e)}")
            raise

    return {"index_created": True}