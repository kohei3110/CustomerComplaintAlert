from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, BlobClient
from datetime import datetime, timedelta
import logging

class BlobStorageService:
    def __init__(self, connection_string):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing BlobStorageService")
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.logger.info(f"BlobServiceClient initialized for account: {self.blob_service_client.account_name}")

    def get_blob_data(self, container_name, blob_name):
        self.logger.info(f"Getting blob data from container: {container_name}, blob: {blob_name}")
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob().readall()
        self.logger.info(f"Blob data read successfully, size: {len(blob_data)} bytes")
        return blob_data.decode('utf-8')

    def get_sas_token(self, container_name, blob_name):
        self.logger.info(f"Generating SAS token for container: {container_name}, blob: {blob_name}")
        expiry_time = datetime.utcnow() + timedelta(minutes=10)
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=self.blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=expiry_time
        )
        self.logger.info(f"SAS token generated successfully, expires at: {expiry_time}")
        return sas_token

    def download_blob(self, container_name, blob_name, sas_token):
        self.logger.info(f"Downloading blob from container: {container_name}, blob: {blob_name}")
        blob_client: BlobClient = self.blob_service_client.get_blob_client(container_name, blob_name)
        sas_url = f"{blob_client.url}?{sas_token}"
        self.logger.debug(f"Using SAS URL: {sas_url[:50]}...")
        blob_client_sas: BlobClient = BlobClient.from_blob_url(blob_url=sas_url)
        blob_data = blob_client_sas.download_blob().readall()
        self.logger.info(f"Blob downloaded successfully, size: {len(blob_data)} bytes")
        return blob_data

    def extract_complaint_details(self, container_name, blob_name):
        """
        Blob を解析して、クレーム内容を取得する
        """
        self.logger.info(f"Extracting complaint details from container: {container_name}, blob: {blob_name}")
        try:
            blob_data = self.get_blob_data(container_name, blob_name)
            
            # クレーム内容を解析するロジックをここに実装
            # 例として、JSON形式のデータを解析する
            import json
            complaint_details = json.loads(blob_data)
            self.logger.info(f"Complaint details extracted successfully from {container_name}/{blob_name}")
            self.logger.debug(f"Extracted complaint details: {complaint_details}")
            
            return complaint_details
        except Exception as e:
            self.logger.error(f"Error extracting complaint details from {container_name}/{blob_name}: {e}", exc_info=True)
            return None