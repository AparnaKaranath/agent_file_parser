import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from src.state.agent_state import AgentState

# Load environment variables from .env file
load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = "file-index"

# -------- NODE 3: UPLOAD DOCUMENTS TO INDEX -----
def upload_to_index(state: AgentState):
    if not SEARCH_ENDPOINT or not SEARCH_KEY:
        raise ValueError("AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_KEY is missing")
    
    documents = state.get("documents", [])
    blob_names = state.get("blob_names", [])
    
    if not documents:
        print("No documents to upload")
        return {
            "documents_uploaded": 0,
            "blob_names": blob_names,
            "upload_status": "no_documents"
        }
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )
    
    try:
        result = search_client.upload_documents(documents)
        print(f"Uploaded {len(documents)} documents from {len(blob_names)} blobs to index '{INDEX_NAME}'")
        print(f"Blob names processed: {blob_names}")
        
        return {
            "documents_uploaded": len(documents),
            "blob_names": blob_names,
            "upload_status": "success"
        }
    except Exception as e:
        print(f"Error uploading documents: {str(e)}")
        return {
            "documents_uploaded": 0,
            "blob_names": blob_names,
            "upload_status": "failed",
            "error": str(e)
        }