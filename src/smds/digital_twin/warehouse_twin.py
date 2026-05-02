from __future__ import annotations

from collections import deque
from typing import Any, Dict, Optional

from .base import DigitalTwinBase
from .enums import WarehouseState


class WarehouseTwin(DigitalTwinBase):
    TOTAL_SLOTS = 200

    def __init__(
        self,
        device_id: str = "WH-001",
        opcua_node_id: str = "ns=2;s=WH-001",
    ):
        super().__init__(device_id, opcua_node_id)
        self.part_a_stock: int = 0
        self.part_b_stock: int = 0
        self.raw_stock_a: float = 500.0
        self.raw_stock_b: float = 300.0
        self.stacker_pos: list = [0.0, 0.0, 0.0]
        self.task_queue: deque = deque()
        self._current_task_time: float = 0.0

    def _initial_state(self) -> WarehouseState:
        return WarehouseState.NORMAL

    def _validate_hardware_state(self, raw: Dict[str, Any]) -> bool:
        stock = raw.get("part_a_stock")
        if stock is not None and (stock < 0 or stock > self.TOTAL_SLOTS):
            return False
        return True

    def _on_sync_success(self, raw_data: Dict[str, Any]):
        for key in ("part_a_stock", "part_b_stock"):
            if key in raw_data:
                setattr(self, key, raw_data[key])
        for key in ("raw_stock_a", "raw_stock_b"):
            if key in raw_data:
                setattr(self, key, raw_data[key])

    def simulate(self, delta_t: float) -> Dict[str, Any]:
        if self.task_queue and self._current_task_time <= 0:
            task = self.task_queue[0]
            self._current_task_time = task["duration"]
            self.stacker_pos = task.get("target_pos", self.stacker_pos)

        if self._current_task_time > 0:
            self._current_task_time -= delta_t
            if self._current_task_time <= 0:
                task = self.task_queue.popleft()
                self._apply_task(task)

        occupancy = (self.part_a_stock + self.part_b_stock) / self.TOTAL_SLOTS
        if occupancy > 0.95:
            self._state = WarehouseState.FULL
        elif self._state == WarehouseState.FULL and occupancy < 0.85:
            self._state = WarehouseState.NORMAL

        return {
            "wh_state": self._state.value,
            "occupancy_rate": round(occupancy * 100, 1),
            "stacker_x": self.stacker_pos[0],
            "stacker_y": self.stacker_pos[1],
            "stacker_z": self.stacker_pos[2],
            "total_slots": self.TOTAL_SLOTS,
            "occupied_slots": self.part_a_stock + self.part_b_stock,
            "part_a_stock": self.part_a_stock,
            "part_b_stock": self.part_b_stock,
            "raw_stock_a": round(self.raw_stock_a, 1),
            "raw_stock_b": round(self.raw_stock_b, 1),
            "task_state": 1 if self.task_queue else 0,
        }

    def _apply_task(self, task: dict):
        op = task.get("operation")
        qty = task.get("quantity", 1)
        if op == "STORE_PART_A":
            self.part_a_stock += qty
        elif op == "STORE_PART_B":
            self.part_b_stock += qty
        elif op == "RETRIEVE_PART_A":
            self.part_a_stock = max(0, self.part_a_stock - qty)
        elif op == "RETRIEVE_PART_B":
            self.part_b_stock = max(0, self.part_b_stock - qty)
        elif op == "STORE_RAW_A":
            self.raw_stock_a += task.get("quantity_kg", 0)
        elif op == "CONSUME_RAW_A":
            self.raw_stock_a = max(0, self.raw_stock_a - task.get("quantity_kg", 0))
        elif op == "CONSUME_RAW_B":
            self.raw_stock_b = max(0, self.raw_stock_b - task.get("quantity_kg", 0))

    # ---------- Polymorphic dispatch ----------

    def is_idle(self) -> bool:
        return True

    def can_accept_task(self, task_type: str) -> bool:
        return task_type in ("STORE", "RETRIEVE")

    # ---------- Public methods ----------

    def store_request(self, material_type: str, quantity: int = 1):
        op_map = {"PART-A": "STORE_PART_A", "PART-B": "STORE_PART_B"}
        self.task_queue.append({
            "operation": op_map.get(material_type, "STORE_PART_A"),
            "quantity": quantity,
            "duration": 30.0,
            "target_pos": [1.5, 2.0, 3.0],
        })

    def retrieve_request(self, material_type: str, quantity: int = 1):
        op_map = {"PART-A": "RETRIEVE_PART_A", "PART-B": "RETRIEVE_PART_B"}
        self.task_queue.append({
            "operation": op_map.get(material_type, "RETRIEVE_PART_A"),
            "quantity": quantity,
            "duration": 30.0,
            "target_pos": [1.5, 2.0, 3.0],
        })
