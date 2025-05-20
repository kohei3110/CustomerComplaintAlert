import json
import logging

import pandas as pd
from azure.eventhub import EventHubConsumerClient
from io import BytesIO
from azure.cosmos import CosmosClient


class EventHubService:


    def __init__(self, connection_string, event_hub_name, consumer_group, blob_storage_service, cosmos_db_service, openai_service, email_service):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing EventHubService with event hub name: {event_hub_name}, consumer group: {consumer_group}")
        self.client = EventHubConsumerClient.from_connection_string(
            conn_str=connection_string,
            consumer_group=consumer_group,
            eventhub_name=event_hub_name
        )
        self.blob_storage_service = blob_storage_service
        self.cosmos_db_service = cosmos_db_service
        self.openai_service = openai_service
        self.email_service = email_service
        self.logger.info("EventHubService initialized successfully")


    def download_blob(self, container_name, blob_name):
        try:
            self.logger.info(f"Downloading blob from container: {container_name}, blob name: {blob_name}")
            sas_token = self.blob_storage_service.get_sas_token(container_name, blob_name)
            blob_data = self.blob_storage_service.download_blob(container_name, blob_name, sas_token)
            self.logger.info(f"Blob downloaded successfully. Size: {len(blob_data) if blob_data else 0} bytes")
            return blob_data
        except Exception as e:
            self.logger.error(f"Error downloading blob: {e}", exc_info=True)
            return None


    def read_excel(self, blob_data):
        try:
            self.logger.info(f"Reading Excel file from blob data")
            df = pd.read_excel(BytesIO(blob_data), engine="openpyxl")
            row_count = len(df) if df is not None else 0
            self.logger.info(f"Excel file read successfully. Row count: {row_count}")
            return df
        except Exception as e:
            self.logger.error(f"Error reading Excel file: {e}", exc_info=True)
            return None


    def on_event(self, partition_context, event):

        try:
            self.logger.info(f"Received event from partition: {partition_context.partition_id}, sequence number: {event.sequence_number}")
            event_data = json.loads(event.body_as_str())
            self.logger.debug(f"Event data: {event_data}")
            
            for item in event_data:
                url = item.get("data").get("url")
                self.logger.info(f"Processing blob URL: {url}")
                url_parts = url.split("/")
                container_name = url_parts[-2]
                blob_name = url_parts[-1]
                
                self.logger.info(f"Downloading blob from container: {container_name}, blob: {blob_name}")
                blob_data = self.download_blob(container_name, blob_name)
                
                if blob_data:
                    self.logger.info(f"Reading Excel data from blob")
                    df = self.read_excel(blob_data)
                    
                    if df is not None:
                        row_count = len(df)
                        self.logger.info(f"Excel data loaded successfully. Row count: {row_count}")
                        
                        self.logger.info(f"Saving data to Cosmos DB")
                        self.cosmos_db_service.save_to_cosmos_db(df)
                        
                        self.logger.info(f"Getting complaint scores from OpenAI")
                        results = self.openai_service.get_complaint_score(df)
                        
                        if results:
                            self.logger.info(f"Received {len(results)} results from OpenAI")
                            for result in results:
                                complaint_id = result.get("id", "unknown")
                                score = result.get("score", "unknown")
                                self.logger.info(f"Processing result for complaint ID: {complaint_id}, score: {score}")
                                
                                # FIXME: ここで結果を Cosmos DB に再保存する
                                if result.get("score") == 5:
                                    self.logger.warning(f"High priority complaint detected (score=5). Sending email alert for complaint ID: {complaint_id}")
                                    self.email_service.send_email(result)
                        else:
                            self.logger.warning("No results returned from OpenAI")
                    else:
                        self.logger.error("Failed to read Excel data from blob")
                else:
                    self.logger.error(f"Failed to download blob from {container_name}/{blob_name}")

            self.logger.info(f"Updating checkpoint for partition: {partition_context.partition_id}, sequence: {event.sequence_number}")
            partition_context.update_checkpoint(event)

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.error(f"Error processing event: {e}", exc_info=True)


    async def start(self):
        self.logger.info("Starting event hub consumer client...")
        await self.client.receive(
            on_event=self.on_event,
            starting_position="-1"
        )