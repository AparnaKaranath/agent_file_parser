from typing import List, Optional, TypedDict, Dict

# AgentState holds the state of the agents, including the current file being processed and its summary
class AgentState(TypedDict):
    #current_file: str
    folder_path: str
    file_contents: str
    uploaded_blob_url: str
    documents: List[dict]
    blob_names: List[str]
    index_created: bool
    index_status: str
    documents_uploaded: int
    upload_status: str
    error: Optional[str]
    #summary: str

