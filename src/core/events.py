import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, listener: Callable):
        """Subscribe a listener to an event."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    async def publish(self, event_type: str, *args, **kwargs):
        """Publish an event to all subscribers concurrently."""
        if event_type in self.listeners:
            tasks = []
            for listener in self.listeners[event_type]:
                tasks.append(asyncio.create_task(listener(*args, **kwargs)))
            if tasks:
                # Fire and forget or wait? Wait ensures data consistency before returning
                # but fire and forget is faster. We wait to ensure profile is created.
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in results:
                    if isinstance(res, Exception):
                        logger.error(f"Event listener for {event_type} failed: {res}")

event_bus = EventBus()
