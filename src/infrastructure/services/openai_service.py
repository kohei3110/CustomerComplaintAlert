import time
import json
import os
import logging

from openai import AzureOpenAI
import pandas as pd

from infrastructure.services.cosmos_db_service import CosmosDbService


# FIXME: インターフェース化して呼び出し先を切り替えられるようにしたい
class OpenAIService:

    _client_instance = None
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("AOAI_API_KEY")
        self.api_endpoint = os.getenv("AOAI_ENDPOINT")
        self.api_version = os.getenv("AOAI_API_VERSION")
        self.deployment = os.getenv("DEPLOYMENT")
        self.cosmos_db_service = CosmosDbService(os.getenv("COSMOS_DB_CONNECTION_STR"))


    @classmethod
    def get_client(cls):
        logger = logging.getLogger(__name__)
        if cls._client_instance is None:
            logger.info("Initializing Azure OpenAI client...")
            cls._client_instance = AzureOpenAI(
                api_version=os.getenv("AOAI_API_VERSION"),
                api_key=os.getenv("AOAI_API_KEY"),
                azure_endpoint=os.getenv("AOAI_ENDPOINT"),
            )
            logger.info("Azure OpenAI client initialized successfully")
        return cls._client_instance


    def get_complaint_score(self, df):
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
            self.logger.info(f"Processing complaint ID: {input['id']} from customer: {input['customer']}")
            
            system_prompt = self.cosmos_db_service.get_system_prompt()
            self.logger.debug(f"Using system prompt: {system_prompt[:50]}...")
            
            self.logger.info(f"Sending request to OpenAI for complaint ID: {input['id']}")
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
            response_content = response.choices[0].message.content
            self.logger.info(f"Received response for complaint ID: {input['id']}")
            self.logger.debug(f"OpenAI response content: {response_content}")
            
            results.append(json.loads(response_content))
            # レート制限回避のため、10秒待機
            self.logger.info(f"Waiting 10 seconds to avoid rate limits...")
            time.sleep(10)
        
        self.logger.info(f"Processing completed. Total results: {len(results)}")
        return results