
from src.state.agent_state import AgentState
from azure.storage.blob import BlobClient
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

import json
import os
from urllib.parse import unquote, urlparse

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

    uploaded_blob_url = state.get("uploaded_blob_url") if isinstance(state, dict) else None
    blob_prefix = state.get("blob_prefix") if isinstance(state, dict) else None
    if uploaded_blob_url:
        blob_path = unquote(urlparse(uploaded_blob_url).path.lstrip("/"))
        container_prefix = f"{container_name}/"
        blob_names_to_read = [blob_path[len(container_prefix):] if blob_path.startswith(container_prefix) else blob_path]
    else:
        blobs = container_client.list_blobs(name_starts_with=blob_prefix) if blob_prefix else container_client.list_blobs()
        blob_names_to_read = [blob_item.name for blob_item in blobs if blob_item.name.lower().endswith(".json")]

    documents = []
    blob_names = []

    for blob_name in blob_names_to_read:
        blob_names.append(blob_name)

        # raw = container_client.get_blob_client(blob=blob_name).download_blob().readall().decode("utf-16")
        data = container_client.get_blob_client(blob=blob_name).download_blob().readall()

        try:
            raw = data.decode("utf-8")
        except UnicodeDecodeError:
            print(f"Skipping non UTF-8 blob: {blob_name}")
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            print(f"Skipping non-JSON blob: {blob_name}")
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