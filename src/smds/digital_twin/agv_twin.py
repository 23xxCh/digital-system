from __future__ import annotations

from typing import Any, Dict, Optional

from .base import DigitalTwinBase
from .configs import AGVConfig
from .enums import AGVState


class AGVTwin(DigitalTwinBase):
    def __init__(
        self,
        device_id: str = "AGV-001",
        opcua_node_id: str = "ns=2;s=AGV-001",
        config: Optional[AGVConfig] = None,
    ):
        super().__init__(device_id, opcua_node_id)
        self.config = config or AGVConfig()
        self.position: list = [0.0, 0.0]
        self.battery: float = 100.0
        self.has_load: bool = False
        self.destination: Optional[str] = None
        self.load_type: Optional[str] = None
        self.load_weight: float = 0.0

    def _initial_state(self) -> AGVState:
        return AGVState.IDLE

    def _validate_hardware_state(self, raw: Dict[str, Any]) -> bool:
        battery = raw.get("battery_level")
        if battery is not None and (battery < -1 or battery > 102):
            return False
        return True

    def simulate(self, delta_t: float) -> Dict[str, Any]:
        if self._state == AGVState.MOVE:
            self.battery -= delta_t * self.config.drain_rate
            self.battery = max(0, self.battery)
        return {
            "agv_state": self._state.value,
            "position_x": round(self.position[0], 1),
            "position_y": round(self.position[1], 1),
            "battery_level": round(self.battery, 2),
            "has_load": self.has_load,
            "destination": self.destination or "",
        }

    # ---------- Polymorphic dispatch ----------

    def is_idle(self) -> bool:
        return self._state == AGVState.IDLE

    def can_accept_task(self, task_type: str) -> bool:
        return self.is_idle() and task_type == "TRANSPORT"

    def assign_task(self, order) -> None:
        self.go_to(order.destination)

    # ---------- Public methods ----------

    def go_to(self, dest: str):
        self.destination = dest
        self._state = AGVState.MOVE

    def needs_charge(self) -> bool:
        return self.battery < self.config.charge_threshold
