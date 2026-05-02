from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, List, Optional

from .exceptions import CommunicationError


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, timeout: float = 5.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0.0

    @property
    def state(self) -> CircuitBreakerState:
        if self._state == CircuitBreakerState.OPEN:
            if time.time() - self._last_failure_time >= self.timeout:
                self._state = CircuitBreakerState.HALF_OPEN
        return self._state

    def allow_request(self) -> bool:
        current = self.state
        if current == CircuitBreakerState.CLOSED:
            return True
        if current == CircuitBreakerState.HALF_OPEN:
            return True
        return False

    def record_success(self):
        if self._state == CircuitBreakerState.HALF_OPEN:
            self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0

    def record_failure(self):
        self._last_failure_time = time.time()
        if self._state == CircuitBreakerState.HALF_OPEN:
            self._state = CircuitBreakerState.OPEN
            return
        self._failure_count += 1
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitBreakerState.OPEN


class OPCUAConnector:
    def __init__(self, server_url: str, circuit_breaker: Optional[CircuitBreaker] = None):
        self.server_url = server_url
        self.subscriptions: Dict[str, List[str]] = {}
        self.circuit_breaker = circuit_breaker or CircuitBreaker()

    async def connect(self):
        raise NotImplementedError("Requires opcua-asyncio runtime")

    async def read_device_nodes(
        self, client: Any, device_id: str, node_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        for logical_name, node_id_str in node_mapping.items():
            try:
                results[logical_name] = None
            except Exception:
                results[logical_name] = None
        return results

    async def fetch_all(self) -> Dict[str, Dict]:
        if not self.circuit_breaker.allow_request():
            raise CommunicationError("Circuit breaker OPEN — OPC UA unavailable")
        try:
            result: Dict[str, Dict] = {}
            self.circuit_breaker.record_success()
            return result
        except Exception:
            self.circuit_breaker.record_failure()
            raise
