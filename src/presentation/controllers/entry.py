import os

from fastapi import BackgroundTasks, FastAPI
from dotenv import load_dotenv

from infrastructure.services.blob_storage_service import BlobStorageService
from infrastructure.services.cosmos_db_service import CosmosDbService
from infrastructure.services.event_hub_service import EventHubService
from application.services.event_processor import EventProcessor
from infrastructure.services.openai_service import OpenAIService


# Load environment variables from .env file
load_dotenv()

app = FastAPI()


async def run_event_processor():
    event_hub_connection_str = os.environ.get("EVENT_HUB_CONNECTION_STR")
    event_hub_name = os.environ.get("EVENT_HUB_NAME")
    consumer_group = "$Default"
    blob_storage_connection_str = os.environ.get("BLOB_STORAGE_CONNECTION_STR")

    blob_storage_service = BlobStorageService(blob_storage_connection_str)
    cosmos_db_service = CosmosDbService(os.environ.get("COSMOS_DB_CONNECTION_STR"))
    openai_service = OpenAIService()
    event_hub_service = EventHubService(
        event_hub_connection_str, event_hub_name, consumer_group, blob_storage_service, cosmos_db_service, openai_service
    )
    event_processor = EventProcessor(event_hub_service)

    print("Starting event processor...")
    await event_processor.start()


@app.on_event("startup")
async def startup_event():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(run_event_processor)
    await run_event_processor()


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)