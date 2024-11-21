from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

class CosmosDbService:


    def __init__(self, connection_string):
        self.cosmos_db_client = CosmosClient.from_connection_string(connection_string)


    def save_to_cosmos_db(self, df):
        for _, row in df.iterrows():
            document = {
                "id": str(row["クレームID"]),
                "complaint": row["クレーム内容"],
                "partner": row["販売パートナー"],
                "customer": row["Cusomter"],
                "product": row["対象製品"],
                "date": row["日付"].isoformat() if hasattr(row["日付"], "isoformat") else row["日付"]
            }
            try:
                self.cosmos_db_client.get_database_client("complaints_db") \
                    .get_container_client("complaints").upsert_item(document)
            except CosmosHttpResponseError as e:
                print(f"Failed to upsert item: {e.message}")
