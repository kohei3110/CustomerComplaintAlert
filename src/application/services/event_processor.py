import logging

class EventProcessor:
    def __init__(self, event_hub_service):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing EventProcessor")
        self.event_hub_service = event_hub_service

    async def start(self):
        self.logger.info("Starting event processor service")
        await self.event_hub_service.start()