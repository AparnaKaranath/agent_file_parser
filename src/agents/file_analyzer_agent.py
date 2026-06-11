from langgraph.graph import StateGraph
from typing import Any, Dict

#from sympy import content
from src.nodes.file_reader_node import FileReaderNode

class FileAnalyzerAgent:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.state_graph = StateGraph()
        print("Initializing FileAnalyzerAgent...")
        self.file_reader = FileReaderNode(file_path)
        content = self.file_reader._read_file(file_path, f".{file_path.split('.')[-1]}")
        print("reading the content")
        return {
            "content": content,
        }