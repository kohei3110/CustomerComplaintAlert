from azure.storage.blob import BlobServiceClient

class BlobStorageService:
    def __init__(self, connection_string):
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def get_blob_data(self, container_name, blob_name):
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob().readall()
        return blob_data.decode('utf-8')