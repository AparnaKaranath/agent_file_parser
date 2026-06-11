from langgraph.graph import StateGraph, START, END
from src.nodes.file_reader_node import FileReaderNode
from src.nodes.blob_read_node import read_blob
from src.nodes.index_creation_node import create_index
from src.nodes.upload_documents_node import upload_to_index
from src.state.agent_state import AgentState

class MainGraph:

    def __init__(self, file_analyzer_agent=None, file_reader=None):
        self.file_analyzer_agent = file_analyzer_agent
        self.file_reader = file_reader
        print("Initializing MainGraph...")

    def build_graph(self):
        """Graph 1: Read files from folder and extract to JSON"""
        print("Building file reading graph...")
        file_reader = FileReaderNode()

        builder = StateGraph(AgentState)
        builder.add_node("file_reader", file_reader)

        builder.add_edge(START, "file_reader")
        builder.add_edge("file_reader", END)
        
        print("File reading graph built successfully.")
        return builder.compile()

    def build_graph_index(self):
        """Graph 2: Read blobs, create index, and upload documents to Azure Search"""
        print("Building blob to index graph...")
        
        builder = StateGraph(AgentState)

        # Add nodes
        builder.add_node("read_blob", read_blob)
        builder.add_node("create_index", create_index)
        builder.add_node("upload_to_index", upload_to_index)

        # Set entry point
        builder.set_entry_point("read_blob")

        # Add edges
        builder.add_edge("read_blob", "create_index")
        builder.add_edge("create_index", "upload_to_index")
        builder.add_edge("upload_to_index", END)

        print("Blob to index graph built successfully.")
        return builder.compile()