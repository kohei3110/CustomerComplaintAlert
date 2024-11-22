import os


# FIXME: インターフェース化して呼び出し先を切り替えられるようにしたい
class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("AOAI_API_KEY")
        self.api_endpoint = os.getenv("AOAI_ENDPOINT")