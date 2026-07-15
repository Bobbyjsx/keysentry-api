import asyncio
import logging
from enum import Enum
from typing import Callable, Dict, List

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    USER_SIGNED_UP = "USER_SIGNED_UP"
    API_KEY_DISCOVERED = "API_KEY_DISCOVERED"
    SCAN_COMPLETED = "SCAN_COMPLETED"
    SCAN_FAILED = "SCAN_FAILED"


class Event:
    def __init__(self, event_type: EventType, **kwargs):
        self.event_type = event_type
        self.kwargs = kwargs


class EventBus:
    def __init__(self):
        self.listeners: Dict[EventType, List[Callable]] = {}

    def subscribe(self, event_type: EventType, listener: Callable):
        """Subscribe a listener to an event."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    async def publish(self, event_type: EventType, *args, **kwargs):
        """Publish an event to all subscribers concurrently."""
        if event_type in self.listeners:
            tasks = []
            for listener in self.listeners[event_type]:
                tasks.append(asyncio.create_task(listener(*args, **kwargs)))
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in results:
                    if isinstance(res, Exception):
                        logger.error(f"Event listener for {event_type} failed: {res}")


event_bus = EventBus()
