from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, BlobClient
from datetime import datetime, timedelta

class BlobStorageService:
    def __init__(self, connection_string):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def get_blob_data(self, container_name, blob_name):
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob().readall()
        return blob_data.decode('utf-8')

    def get_sas_token(self, container_name, blob_name):
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=self.blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=10)
        )
        return sas_token

    def download_blob(self, container_name, blob_name, sas_token):
        blob_client: BlobClient = self.blob_service_client.get_blob_client(container_name, blob_name)
        sas_url = f"{blob_client.url}?{sas_token}"
        blob_client_sas: BlobClient = BlobClient.from_blob_url(blob_url=sas_url)
        blob_data = blob_client_sas.download_blob().readall()
        return blob_data