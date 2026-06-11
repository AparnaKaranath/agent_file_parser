import os
import glob
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import PyPDF2
import docx
from src.state.agent_state import AgentState
from src.service.blob.blob_connection import BlobConnection

class FileReaderNode:
    def __call__(self, state: AgentState) -> AgentState:
        """Reads supported files, extracts text, converts to JSON chunks, and uploads JSON to blob."""
        print("getting the path")
        folder_path = state["folder_path"]
        print(f"Reading files from folder: {folder_path}")
        
        if not os.path.isdir(folder_path):
            print(f"Error: Folder path does not exist: {folder_path}")
            return {
                "folder_path": folder_path,
                "file_contents": "[]",
                "uploaded_blob_url": ""
            }
        
        file_patterns = ["*.txt", "*.pdf", "*.docx", "*.doc", "*.xlsx", "*.xls", "*.csv"]
        all_files = []

        for pattern in file_patterns:
            matched_files = glob.glob(os.path.join(folder_path, "**", pattern), recursive=True)
            all_files.extend(matched_files)
            print(f"Pattern '{pattern}': Found {len(matched_files)} files")
        
        print(f"All files found: {all_files}")
        print(f"Found {len(all_files)} files in {folder_path}")

        # Build JSON records in required format:
        # [{"id":"doc1_1","content":"...","file_name":"file1.pdf"}, ...]
        json_records = []
        for file_index, file_path in enumerate(all_files, start=1):
            file_ext = Path(file_path).suffix.lower()
            content = self._read_file(file_path, file_ext)
            file_name = Path(file_path).name

            for chunk_index, chunk in enumerate(self._chunk_text(content), start=1):
                if chunk.strip():
                    json_records.append({
                        "id": f"doc{file_index}_{chunk_index}",
                        "content": chunk,
                        "file_name": file_name
                    })

        json_content = json.dumps(json_records, ensure_ascii=False, indent=2)
        uploaded_blob_url = ""

        connection_string = os.environ.get("STR_BLOB_CONNECTION_STRING")
        container_name = os.environ.get("STR_BLOB_CONTAINER_NAME")
        print("connection string###",connection_string)
        print("connection string###",container_name)
        if connection_string and container_name and json_records:
            print(
                "Uploading extracted JSON to blob storage..., ",
                f"Connection String: {'***' if connection_string else 'Not Set'}, Container Name: {container_name}"
            )
            blob_connection = BlobConnection(connection_string, container_name)
            blob_name = f"file_contents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            uploaded_blob_url = blob_connection.upload_text(json_content, blob_name)
            print(f"Uploaded extracted JSON to: {uploaded_blob_url}")

        return {
            "folder_path": folder_path,
            "file_contents": json_content,  # now JSON string
            "uploaded_blob_url": uploaded_blob_url
        }

    def _chunk_text(self, text: str, chunk_size: int = 2000):
        if not text:
            return []
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    def _read_file(self, file_path: str, file_ext: str) -> str:
        try:
            if file_ext == ".txt":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()

            elif file_ext == ".pdf":
                content = ""
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        content += page.extract_text() or ""
                return content

            elif file_ext in [".docx", ".doc"]:
                doc = docx.Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])

            elif file_ext in [".xlsx", ".xls"]:
                excel_file = pd.ExcelFile(file_path)
                sheets = []
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    sheets.append(f"Sheet: {sheet_name}\n{df.to_string(max_rows=50)}")
                return "\n\n".join(sheets)

            elif file_ext == ".csv":
                df = pd.read_csv(file_path)
                return df.to_string(max_rows=50)

        except Exception as e:
            return f"Error reading file: {str(e)}"

        return ""