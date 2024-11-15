import json

from azure.eventhub import EventHubConsumerClient


class EventHubService:


    def __init__(self, connection_string, event_hub_name, consumer_group, blob_storage_service):
        self.client = EventHubConsumerClient.from_connection_string(
            conn_str=connection_string,
            consumer_group=consumer_group,
            eventhub_name=event_hub_name
        )
        self.blob_storage_service = blob_storage_service


    def on_event(self, partition_context, event):

        try:
            event_data = json.loads(event.body_as_str())
            print(f"Received event: {event_data}")
            for item in event_data:
                url = item.get("data").get("url")
                print(f"Received blob url: {url}")

            # チェックポイントを更新して、イベントが再度処理されないようにする
            partition_context.update_checkpoint(event)

            # TODO: SAS を取得して、Blob をダウンロードする
            # TODO: Blob を解析して、クレーム内容を取得する
            # TODO: クレーム内容を Azure OpenAI で構造化する
            # TODO: クレーム内容を Cosmos DB に保存する
            # TODO: 一定の条件を満たしたら、メールを送信する

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error processing event: {e}")


    async def start(self):
        await self.client.receive(
            on_event=self.on_event,
            starting_position="-1"  # "-1" is from the beginning of the partition.
        )