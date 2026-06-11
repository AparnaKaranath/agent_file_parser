
from src.state.agent_state import AgentState
from azure.storage.blob import BlobClient
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

import json
import os

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from src.state.agent_state import AgentState

# Load environment variables from .env file
load_dotenv()

connection_string = os.getenv("STR_BLOB_CONNECTION_STRING")
container_name = os.getenv("STR_BLOB_CONTAINER_NAME")

def read_blob(state: AgentState):
    if not connection_string:
        raise ValueError("STR_BLOB_CONNECTION_STRING is missing")
    if not container_name:
        raise ValueError("STR_BLOB_CONTAINER_NAME is missing")

    service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = service_client.get_container_client(container_name)

    blob_prefix = state.get("blob_prefix") if isinstance(state, dict) else None
    blobs = container_client.list_blobs(name_starts_with=blob_prefix) if blob_prefix else container_client.list_blobs()

    documents = []
    blob_names = []

    for blob_item in blobs:
        blob_name = blob_item.name
        blob_names.append(blob_name)

        # raw = container_client.get_blob_client(blob=blob_name).download_blob().readall().decode("utf-16")
        data = container_client.get_blob_client(blob=blob_name).download_blob().readall()

        try:
            raw = data.decode("utf-8")
        except UnicodeDecodeError:
            print("Not UTF-8 text")
            raw = None
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, list):
            for doc in parsed:
                if isinstance(doc, dict):
                    documents.append(doc)
        elif isinstance(parsed, dict):
            parsed["source_blob"] = blob_name
            documents.append(parsed)

    for i, doc in enumerate(documents, start=1):
        doc["index"] = i

    return {"documents": documents, "blob_names": blob_names}