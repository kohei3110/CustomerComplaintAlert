import json

import pandas as pd
from azure.eventhub import EventHubConsumerClient
from io import BytesIO
from azure.cosmos import CosmosClient


class EventHubService:


    def __init__(self, connection_string, event_hub_name, consumer_group, blob_storage_service, cosmos_db_service):
        self.client = EventHubConsumerClient.from_connection_string(
            conn_str=connection_string,
            consumer_group=consumer_group,
            eventhub_name=event_hub_name
        )
        self.blob_storage_service = blob_storage_service
        self.cosmos_db_service = cosmos_db_service


    def download_blob(self, container_name, blob_name):
        try:
            sas_token = self.blob_storage_service.get_sas_token(container_name, blob_name)
            blob_data = self.blob_storage_service.download_blob(container_name, blob_name, sas_token)
            return blob_data
        except Exception as e:
            print(f"Error downloading blob: {e}")
            return None


    def read_excel(self, blob_data):
        try:
            df = pd.read_excel(BytesIO(blob_data), engine="openpyxl")
            return df
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return None


    def on_event(self, partition_context, event):

        try:
            event_data = json.loads(event.body_as_str())
            print(f"Received event: {event_data}")
            for item in event_data:
                url = item.get("data").get("url")
                print(f"Received blob url: {url}")
                url_parts = url.split("/")
                container_name = url_parts[-2]
                blob_name = url_parts[-1]
                blob_data = self.download_blob(container_name, blob_name)
                if blob_data:
                    df = self.read_excel(blob_data)
                    if df is not None:
                        print(f"Excel data: {df}")
                        self.cosmos_db_service.save_to_cosmos_db(df)
                    else:
                        print("Excel data is None")

            partition_context.update_checkpoint(event)

            # TODO: クレーム内容を Azure OpenAI で構造化する

            # TODO: 一定の条件を満たしたら、メールを送信する

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error processing event: {e}")


    async def start(self):
        await self.client.receive(
            on_event=self.on_event,
            starting_position="-1"
        )