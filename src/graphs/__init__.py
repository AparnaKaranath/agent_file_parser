"""
Azure Blob Storage Service Module

This module provides a service class for interacting with Azure Blob Storage.
It handles file upload, download.

Dependencies:
    - azure.storage.blob: Azure Blob Storage SDK
    - azure.identity: Azure authentication library
    - service.KeyVault.keyvault_service: Custom key vault service for secrets management
"""
import os
import logging
from os.path import join as os_path_join
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
class BlobService:
    """
    Azure Blob Storage Service Class
    
    Provides methods for uploading, downloading, and managing files in Azure Blob Storage.
    Supports authentication via connection string or managed identity.
    
    Attributes:
        connection_string (str): Azure Storage connection string
        container_name (str): Name of the blob container
        blob_url (str): Base URL for the blob storage account
        blob_name (str): Name of the current blob being processed
    """        
    def __init__(self, connection_string: str = None, container_name: str = None, mi_client_id: str = None):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_url = None
        self.blob_name = None

        if connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            print("Initialized BlobService with connection string.")
        elif mi_client_id:
            credential = DefaultAzureCredential(managed_identity_client_id=mi_client_id)
            self.blob_service_client = BlobServiceClient(account_url=self.blob_url, credential=credential)
            print("Initialized BlobService with managed identity.")
        else:
            raise ValueError("Either connection string or managed identity client ID must be provided.")
        

    
    def download_blob(self, blob_url, file_name):
        """
        Download a blob from Azure Storage to local file system.
        
        Args:
            blob_url (str): Complete URL of the blob to download
            file_name (str): Name to save the downloaded file as
            
        Returns:
            str: Path to the downloaded file
            
        Raises:
            Exception: If download fails or blob doesn't exist
            
        Example:
            >>> service.download_blob("https://account.blob.core.windows.net/container/file.pdf", "local_file.pdf")
            "Sample/local_file.pdf"
        """
        try:
            # Parse the blob URL to extract components
            blob_details = self.parse_blob_url(blob_url)
            self.blob_url = blob_details['base_url']
            self.container_name = blob_details['container']
            blob_name = blob_details['blob']
            self.blob_name = self.safe_blob_unquote(blob_name)
            # blob_name = f"Content_files/Uploads/Test_Uploads/Xtracto/{file_name}"
            print("########## Logging: In download ##########", flush=True)

            # Create local download directory and file path
            folder_path = "Sample"
            download_path = os_path_join(folder_path, file_name)
            os.makedirs(folder_path, exist_ok=True)

            # Get authenticated blob service client
            blob_service_client = self._get_blob_service_client()
            print("########## Logging: Connecting to blob ##########", flush=True)
            print(f"[FILE] Downloading file: {file_name}", flush=True)

            # Create blob client for specific blob
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=self.blob_name)
            print("Connection created successfully ########## Logging ##########", flush=True)

            # Download blob content to local file
            with open(download_path, "wb") as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())

            print(f" Blob '{self.blob_name}' downloaded to '{download_path}'.", flush=True)
            logging.info(f"Blob {self.blob_name} downloaded successfully to {download_path}.")
            return download_path
        except Exception as ex:
            print(f" Exception in download_blob: {ex}", flush=True)
            logging.error(f"Error in download_blob: {ex}")
            raise

    def upload_blob(self, upload_file_path, file_name):
        """
        Upload a local file to Azure Blob Storage.
        
        Args:
            upload_file_path (str): Path to the local file to upload
            file_name (str): Name to save the file as in blob storage
            
        Returns:
            str: URL of the uploaded blob
            
        Raises:
            Exception: If upload fails or file doesn't exist
            
        Example:
            >>> service.upload_blob("local/file.pdf", "uploaded_file.pdf")
            "https://account.blob.core.windows.net/container/path/uploaded_file.pdf"
        """
        try:
            # Construct blob path using existing blob directory structure
            blob_name = self.blob_name
            print(blob_name,'11')  # Debug logging
            
            # Get the folder path from existing blob name and append new file name
            foldername = os.path.normpath(os.path.dirname(blob_name))
            blob_name = foldername + '/' + file_name
            print(blob_name,'22')  # Debug logging
            print("########## Logging: Upload starting ##########", flush=True)

            # Get authenticated blob service client
            blob_service_client = self._get_blob_service_client() 
            blob_client = blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)

            # Upload file content to blob storage (overwrite if exists)
            with open(upload_file_path, "rb") as upload_file:
                blob_client.upload_blob(upload_file, overwrite=True)
                
            # Get the URL of the uploaded blob
            blob_url = blob_client.url
            print(f"Blob '{blob_name}' uploaded successfully to container '{self.container_name}'.", flush=True)
            logging.info(f"Blob '{blob_name}' uploaded successfully to the '{self.container_name}' container.")
            return blob_url
        except Exception as ex:
            print(f" Exception in upload_blob: {ex}", flush=True)
            logging.error(f"Error in upload_blob: {ex}")
            raise