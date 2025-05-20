from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
import logging

class CosmosDbService:


    def __init__(self, connection_string):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing CosmosDbService")
        self.cosmos_db_client = CosmosClient.from_connection_string(connection_string)
        self.logger.info("CosmosDB client initialized successfully")


    def save_to_cosmos_db(self, df):
        self.logger.info(f"Saving {len(df)} records to Cosmos DB")
        for _, row in df.iterrows():
            document = {
                "id": str(row["クレームID"]),
                "complaint": row["クレーム内容"],
                "partner": row["販売パートナー"],
                "customer": row["Cusomter"],
                "product": row["対象製品"],
                "date": row["日付"].isoformat() if hasattr(row["日付"], "isoformat") else row["日付"],
                "score": row.get("score", None)
            }
            try:
                self.logger.debug(f"Upserting document with ID: {document['id']}")
                self.cosmos_db_client.get_database_client("complaints_db") \
                    .get_container_client("complaints").upsert_item(document)
                self.logger.info(f"Document with ID: {document['id']} upserted successfully")
            except CosmosHttpResponseError as e:
                self.logger.error(f"Failed to upsert item with ID {document['id']}: {e.message}", exc_info=True)


    def get_system_prompt(self):
        self.logger.info("Retrieving system prompt from Cosmos DB")
        try:
            self.logger.debug("Querying prompts container for latest version")
            response = self.cosmos_db_client.get_database_client("complaints_db") \
                    .get_container_client("prompts").query_items(
                        query="SELECT * FROM c WHERE c.version = 'latest'",
                    )
            for item in response:
                prompt = item.get("prompt")
                self.logger.info("System prompt retrieved successfully")
                self.logger.debug(f"Retrieved prompt (first 50 chars): {prompt[:50]}...")
                return prompt
        except CosmosHttpResponseError as e:
            self.logger.error(f"Failed to query items for system prompt: {e.message}", exc_info=True)
            self.logger.info("Using default system prompt")
            # Default system prompt
            return """
                お客様からの苦情内容を、不満度合いに基づいて1から5のスコアで評価してください。スコア5は最も不満が高いことを示します。

                # ステップ

                1. 苦情内容を読み取り、主な問題点を特定します。
                2. 苦情の感情的強度、具体性、影響度などを考慮します。
                3. 不満度合いに従って1から5のスコアを割り当てます。

                # 入力フォーマット

                ```json
                {

                "id": "[id]",
                "complaint": "[苦情内容]",

                "partner": "[販売パートナー]",

                "customer": "[お客様名]",

                "product": "[対象製品]",

                "date": "[日付]"
                }
                ```

                # 出力フォーマット

                - スコア: JSON形式で以下の構造で出力してください。
                ```json
                {

                "id": "[id]",
                "complaint": "[苦情内容]",

                "partner": "[販売パートナー]",

                "customer": "[お客様名]",

                "product": "[対象製品]",

                "date": "[日付]",
                "score": [スコア値]
                }
                ```

                # 例

                **入力例:**
                {

                "id": "CLM-0001",
                "complaint": "搬入が遅れたため、業務開始が遅れた",

                "partner": "株式会社通信販売",

                "customer": "頂点性能産業株式会社",

                "product": "TX-2002",

                "date": "2024-01-02"
                }


                **出力例:**
                ```json
                {

                "id": "CLM-0001",
                "complaint": "搬入が遅れたため、業務開始が遅れた",

                "partner": "株式会社通信販売",

                "customer": "頂点性能産業株式会社",

                "product": "TX-2002",

                "date": "2024-01-02",
                "score": 5
                }
                ```



                # 注意



                - 感情の強さや不満の深刻さを考慮してスコアリングを行ってください。
                - 模糊した苦情は中間のスコアを、具体的かつ影響が大きい苦情は高いスコアを割り当てます。
            """