from src.graphs.main_graph import MainGraph
from pathlib import Path


def main():
    graph = MainGraph()
    project_root = Path(__file__).resolve().parent
    samples_path = project_root / "data" / "samples"

    # ===== GRAPH 1: Read files from folder and upload JSON to blob =====
    print("\n===== GRAPH 1: Reading Files =====")
    initial_state = {
        "folder_path": str(samples_path),
        "file_contents": "",
        "uploaded_blob_url": ""
    }

    file_graph = graph.build_graph()
    result = file_graph.invoke(initial_state)
    
    print(f"\nUploaded blob URL: {result.get('uploaded_blob_url', 'N/A')}")
    print(f"File contents length: {len(result.get('file_contents', ''))} chars")

    # ===== GRAPH 2: Read from blob, create index, upload to search =====
    print("\n===== GRAPH 2: Indexing Documents =====")
    index_state = {
        "documents": [],
        "blob_names": [],
        "uploaded_blob_url": result.get("uploaded_blob_url", ""),
        "index_created": False,
        "index_status": "",
        "documents_uploaded": 0,
        "upload_status": ""
    }

    index_graph = graph.build_graph_index()
    index_result = index_graph.invoke(index_state)

    print(f"\nDocuments uploaded: {index_result.get('documents_uploaded', 0)}")
    print(f"Blobs processed: {index_result.get('blob_names', [])}")
    print(f"Upload status: {index_result.get('upload_status', 'unknown')}")


if __name__ == "__main__":
    main()