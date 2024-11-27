from dataclasses import dataclass
from enum import Enum
from heapq import heappop, heappush
from typing import Any, Dict


class EventType(Enum):
    CUSTOMER_ARRIVAL = "customer"
    ORDER_ARRIVAL = "order"

@dataclass
class Event:
    time: float
    type: EventType
    data: Dict[str, Any]
    
    def __lt__(self, other):
        return self.time < other.time

class EventQueue:
    def __init__(self):
        self.events = []
    
    def add_event(self, event: Event) -> None:
        heappush(self.events, event)
    
    def get_next_event(self) -> Event:
        if self.events:
            return heappop(self.events)
        return None
    
    def peek_next_time(self) -> float:
        if self.events:
            return self.events[0].time
        return float('inf') 