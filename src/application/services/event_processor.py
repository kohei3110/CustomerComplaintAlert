class EventProcessor:
    def __init__(self, event_hub_service):
        self.event_hub_service = event_hub_service

    async def start(self):
        await self.event_hub_service.start()