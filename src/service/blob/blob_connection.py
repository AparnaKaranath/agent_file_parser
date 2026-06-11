import logging
import os
from os.path import join as os_path_join
from dotenv import load_dotenv

from azure.storage.blob import BlobServiceClient, ContentSettings

# Load environment variables from .env file
load_dotenv()

class BlobConnection:
    def __init__(self, connection_string: str = None, container_name: str = None):
        self.connection_string = connection_string or os.environ.get("STR_BLOB_CONNECTION_STRING")
        self.container_name = container_name or os.environ.get("STR_BLOB_CONTAINER_NAME")
        self.blob_url = os.environ.get("STR_BLOB_URL")
        self.blob_name = None

    def _get_blob_service_client(self) -> BlobServiceClient:
        if not self.connection_string:
            raise ValueError("Blob connection string is missing.")
        return BlobServiceClient.from_connection_string(self.connection_string)

    def upload_text(self, content: str, blob_name: str) -> str:
        try:
            if not self.container_name:
                raise ValueError("Blob container name is missing.")

            blob_service_client = self._get_blob_service_client()
            blob_client = blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            blob_client.upload_blob(
                content.encode("utf-8"),
                overwrite=True,
                content_settings=ContentSettings(content_type="text/plain; charset=utf-8")
            )

            logging.info(f"Text uploaded successfully to blob: {blob_name}")
            return blob_client.url
        except Exception as ex:
            logging.error(f"Error in upload_text: {ex}")
            raise

    def download_blob(self, blob_url, file_name):
        try:
            self.blob_url = blob_url
            self.container_name = os.environ.get("STR_BLOB_CONTAINER_NAME")
            self.blob_name = os.path.basename(blob_url)

            folder_path = "Sample"
            download_path = os_path_join(folder_path, file_name)
            os.makedirs(folder_path, exist_ok=True)

            blob_service_client = self._get_blob_service_client()
            blob_client = blob_service_client.get_blob_client(
                container=self.container_name,
                blob=self.blob_name
            )

            with open(download_path, "wb") as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())

            logging.info(f"Blob {self.blob_name} downloaded successfully to {download_path}.")
            return download_path
        except Exception as ex:
            logging.error(f"Error in download_blob: {ex}")
            raise

    def upload_blob(self, upload_file_path, file_name):
        try:
            blob_name = file_name
            blob_service_client = self._get_blob_service_client()
            blob_client = blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            with open(upload_file_path, "rb") as upload_file:
                blob_client.upload_blob(upload_file, overwrite=True)

            blob_url = blob_client.url
            logging.info(f"Blob '{blob_name}' uploaded successfully to the '{self.container_name}' container.")
            return blob_url
        except Exception as ex:
            logging.error(f"Error in upload_blob: {ex}")
            raise