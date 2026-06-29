from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventBus:
    """Small synchronous event bus for later systems without coupling modules."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[[dict[str, Any]], None]) -> None:
        self._listeners[event_name].append(callback)

    def publish(self, event_name: str, payload: dict[str, Any] | None = None) -> None:
        for callback in self._listeners.get(event_name, []):
            callback(payload or {})
