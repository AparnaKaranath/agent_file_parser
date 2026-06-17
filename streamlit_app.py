from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from src.agents.search_query_agent import SearchQueryAgent
from src.graphs.main_graph import MainGraph


SUPPORTED_FILE_TYPES = ["txt", "pdf", "docx", "doc", "xlsx", "xls", "csv"]


def index_uploaded_files(uploaded_files):
    with TemporaryDirectory() as temp_dir:
        upload_dir = Path(temp_dir)

        for uploaded_file in uploaded_files:
            file_path = upload_dir / uploaded_file.name
            file_path.write_bytes(uploaded_file.getbuffer())

        graph = MainGraph()
        file_graph = graph.build_graph()
        file_result = file_graph.invoke(
            {
                "folder_path": str(upload_dir),
                "file_contents": "",
                "uploaded_blob_url": "",
            }
        )

        index_graph = graph.build_graph_index()
        return index_graph.invoke(
            {
                "documents": [],
                "blob_names": [],
                "uploaded_blob_url": file_result.get("uploaded_blob_url", ""),
                "index_created": False,
                "index_status": "",
                "documents_uploaded": 0,
                "upload_status": "",
            }
        )


st.set_page_config(page_title="File Parser Search", page_icon="search", layout="wide")

st.title("File Parser Search")
st.write("Upload files to Azure AI Search, then query the indexed content.")

with st.sidebar:
    st.header("Upload Files")
    uploaded_files = st.file_uploader(
        "Choose files",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
    )

    if st.button("Upload to Index", disabled=not uploaded_files):
        with st.spinner("Reading files and uploading documents to Azure AI Search..."):
            try:
                result = index_uploaded_files(uploaded_files)
                st.session_state["last_index_result"] = result
                st.success("Upload and indexing completed.")
            except Exception as exc:
                st.error(f"Indexing failed: {exc}")

    if "last_index_result" in st.session_state:
        result = st.session_state["last_index_result"]
        st.subheader("Last Upload")
        st.write(f"Index status: `{result.get('index_status', 'unknown')}`")
        st.write(f"Documents uploaded: `{result.get('documents_uploaded', 0)}`")
        st.write(f"Upload status: `{result.get('upload_status', 'unknown')}`")

st.header("Query Index")
question = st.text_input("Ask a question or search for text in uploaded files")
top = st.slider("Number of results", min_value=1, max_value=10, value=5)

if st.button("Search", disabled=not question.strip()):
    with st.spinner("Searching Azure AI Search..."):
        try:
            agent = SearchQueryAgent()
            results = agent.query(question, top=top)
        except Exception as exc:
            st.error(f"Search failed: {exc}")
        else:
            if not results:
                st.info("No matching documents found.")
            else:
                st.success(f"Found {len(results)} result(s).")
                for idx, result in enumerate(results, start=1):
                    title = result.get("file_name") or "Unknown file"
                    score = result.get("score")
                    with st.expander(f"{idx}. {title} | score: {score}"):
                        st.write(result.get("content") or "")
                        st.caption(f"Document ID: {result.get('id')}")
