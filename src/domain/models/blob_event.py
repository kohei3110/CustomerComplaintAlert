class BlobEvent:
    def __init__(self, container_name, blob_name):
        self.container_name = container_name
        self.blob_name = blob_name