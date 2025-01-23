import time
import json
import os

from openai import AzureOpenAI
import pandas as pd

from infrastructure.services.cosmos_db_service import CosmosDbService


# FIXME: インターフェース化して呼び出し先を切り替えられるようにしたい
class OpenAIService:

    _client_instance = None


    def __init__(self):
        self.api_key = os.getenv("AOAI_API_KEY")
        self.api_endpoint = os.getenv("AOAI_ENDPOINT")
        self.api_version = os.getenv("AOAI_API_VERSION")
        self.deployment = os.getenv("DEPLOYMENT")
        self.cosmos_db_service = CosmosDbService(os.getenv("COSMOS_DB_CONNECTION_STR"))


    @classmethod
    def get_client(cls):
        if cls._client_instance is None:
            cls._client_instance = AzureOpenAI(
                api_version=os.getenv("AOAI_API_VERSION"),
                api_key=os.getenv("AOAI_API_KEY"),
                azure_endpoint=os.getenv("AOAI_ENDPOINT"),
            )
        return cls._client_instance


    def get_complaint_score(self, df):
        try:
            client = self.get_client()
            results = []
            for _, row in df.iterrows():
                input = {
                    "id": str(row["クレームID"]),
                    "complaint": row["クレーム内容"],
                    "partner": row["販売パートナー"],
                    "customer": row["Cusomter"],
                    "product": row["対象製品"],
                    "date": row["日付"].isoformat() if hasattr(row["日付"], "isoformat") else row["日付"]
                }
                system_prompt = self.cosmos_db_service.get_system_prompt()
                response = client.chat.completions.create(
                    model=self.deployment,
                    response_format={ "type": "json_object" },
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": str(input),
                        }
                    ]
                )
                print(f"Result: {response.choices[0].message.content}")
                results.append(json.loads(response.choices[0].message.content))
                # レート制限回避のため、10秒待機
                time.sleep(10)
            return results
        except Exception as e:
            print(f"Error getting complaint score: {e}")
            return None
