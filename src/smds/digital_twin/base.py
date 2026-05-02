from abc import ABC, abstractmethod
from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, Optional

from .models import DataPoint, DataShadow


class DigitalTwinBase(ABC):
    def __init__(self, device_id: str, opcua_node_id: str):
        self.device_id = device_id
        self.opcua_node_id = opcua_node_id
        self.shadow = DataShadow(device_id)
        self._state: IntEnum = self._initial_state()
        self._last_sync: Optional[datetime] = None
        self._error: Optional[str] = None

    # ---------- Abstract methods ----------

    @abstractmethod
    def _initial_state(self) -> IntEnum: ...

    @abstractmethod
    def _validate_hardware_state(self, raw: Dict[str, Any]) -> bool: ...

    @abstractmethod
    def simulate(self, delta_t: float) -> Dict[str, Any]: ...

    # ---------- Polymorphic dispatch (engineering review #4) ----------

    def is_idle(self) -> bool:
        return self._state.value == 0

    def can_accept_task(self, task_type: str) -> bool:
        return self.is_idle()

    def assign_task(self, order: Any) -> None:
        raise NotImplementedError(f"{self.__class__.__name__}.assign_task not implemented")

    # ---------- Sync logic ----------

    def sync_from_physical(self, raw_data: Dict[str, Any]) -> bool:
        self._last_sync = datetime.now()
        self._error = None

        if not self._validate_hardware_state(raw_data):
            self._error = f"HARDWARE_VALIDATION_FAILED for {self.device_id}"
            self.shadow.record("sync_status", DataPoint.error(self._error))
            return False

        for key, value in raw_data.items():
            if value is None:
                dp = DataPoint.nil()
            elif isinstance(value, (list, dict, str)) and len(value) == 0:
                dp = DataPoint.empty()
            elif isinstance(value, (int, float)) and value < -900:
                dp = DataPoint.error(f"SENSOR_OUT_OF_RANGE:{key}")
            else:
                dp = DataPoint.happy(value)
            self.shadow.record(key, dp)

        self._on_sync_success(raw_data)
        self.shadow.record("sync_status", DataPoint.happy(True))
        return True

    def _on_sync_success(self, raw_data: Dict[str, Any]):
        pass

    def get_state(self) -> IntEnum:
        return self._state

    def health_report(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "state": self._state.name,
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
            "error": self._error,
            "shadow_keys": list(self.shadow.history.keys()),
        }
