from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Order:
    order_id: str
    part_type: str           # "PART-A" | "PART-B"
    operation: str           # "OP10" | "OP20" | "TRANSPORT" | "LOAD" | "UNLOAD"
    program: str             # G-code filename
    target_pose: Optional[Tuple[float, ...]] = None
    destination: Optional[str] = None
    estimated_duration: float = 240.0
    due_time: Optional[float] = None
    assigned_device: Optional[str] = None
    started_at: Optional[float] = None
    completed: bool = False
    _rewarded: bool = False


class OrderManager:
    def __init__(self):
        self.orders: List[Order] = []
        self.completed: List[Order] = []

    def generate_default_orders(self, count: int = 10) -> List[Order]:
        orders = []
        for i in range(count):
            part_type = "PART-A" if i % 2 == 0 else "PART-B"
            program = "PART-A_OP1.nc" if part_type == "PART-A" else "PART-B_OP1.nc"
            duration = 240.0 if part_type == "PART-A" else 210.0
            orders.append(Order(
                order_id=f"WO-{i+1:04d}",
                part_type=part_type,
                operation="OP10",
                program=program,
                estimated_duration=duration,
            ))
        self.orders = orders
        return orders

    def find_best_task(self, device_id: str) -> Optional[Order]:
        candidates = [o for o in self.orders if not o.assigned_device and self._task_fits_device(o, device_id)]
        if not candidates:
            return None
        return min(candidates, key=lambda o: o.estimated_duration)

    def _task_fits_device(self, order: Order, device_id: str) -> bool:
        if device_id.startswith("CNC"):
            return order.part_type in ("PART-A", "PART-B")
        if device_id.startswith("ROB"):
            return order.operation in ("LOAD", "UNLOAD")
        if device_id.startswith("AGV"):
            return order.operation == "TRANSPORT"
        return False

    def mark_completed(self, order: Order):
        order.completed = True
        self.completed.append(order)

    def get_pending(self) -> List[Order]:
        return [o for o in self.orders if not o.completed and not o.assigned_device]
