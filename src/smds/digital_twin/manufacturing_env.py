from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .manager import DigitalTwinManager
from .order_manager import Order, OrderManager
from .reward_calculator import RewardCalculator

# Device ordering for state encoding and action dispatch
DEVICE_IDS = ["CNC-001", "CNC-002", "CNC-003", "ROB-001", "ROB-002", "AGV-001", "WH-001"]
N_TASKS_MAX = 20  # max tasks in factorized action space


class ManufacturingEnv:
    def __init__(
        self,
        dt_manager: DigitalTwinManager,
        order_manager: Optional[OrderManager] = None,
        reward_calculator: Optional[RewardCalculator] = None,
    ):
        self.dt = dt_manager
        self.om = order_manager or OrderManager()
        self.rc = reward_calculator or RewardCalculator()
        self.current_time: float = 0.0
        self._step_count: int = 0

    def reset(self, orders: Optional[List[Order]] = None) -> np.ndarray:
        self.current_time = 0.0
        self._step_count = 0
        if orders is not None:
            self.om.orders = orders
            self.om.completed.clear()
        elif not self.om.orders:
            self.om.generate_default_orders()
        for twin in self.dt._twins.values():
            twin._state = twin._initial_state()
        return self._encode_state()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, dict]:
        prev_metrics = self._get_metrics()
        self._execute_action(action)

        delta_t = 30.0
        self.current_time += delta_t
        sim_data = self.dt.simulate_all(delta_t)

        for dev_id, data in sim_data.items():
            twin = self.dt.get(dev_id)
            if twin:
                twin._on_sync_success(data)

        next_metrics = self._get_metrics()
        reward = self.rc.compute(next_metrics, self.om.orders, prev_metrics, self.current_time)

        self._step_count += 1
        done = len(self.om.completed) >= len(self.om.orders) or self._step_count > 1000

        return (
            self._encode_state(),
            reward,
            done,
            {"completed": len(self.om.completed), "step": self._step_count},
        )

    def _encode_state(self) -> np.ndarray:
        vec = []
        for dev_id in DEVICE_IDS:
            twin = self.dt.get(dev_id)
            state_val = twin.get_state().value if twin else 0
            state_onehot = [0] * 6
            state_onehot[min(state_val, 5)] = 1

            has_active = 0.0
            if twin and twin.is_idle() is False:
                has_active = 1.0

            queue_len = len([o for o in self.om.orders if not o.assigned_device and self.om._task_fits_device(o, dev_id)])
            tool_life = 100.0
            if twin and hasattr(twin, "tool_life") and twin.tool_life:
                tool_life = min(twin.tool_life)

            vec.extend(state_onehot + [
                float(has_active),
                float(queue_len) / 10,
                tool_life / 100,
            ])

        demand_a = sum(1 for o in self.om.orders if o.part_type == "PART-A" and not o.completed)
        demand_b = sum(1 for o in self.om.orders if o.part_type == "PART-B" and not o.completed)
        vec.extend([
            demand_a / 50.0,
            demand_b / 50.0,
            self.current_time / 86400,
            self._compute_total_energy() / 500.0,
        ])

        return np.array(vec, dtype=np.float32)

    def _execute_action(self, action: int):
        device_idx = action // N_TASKS_MAX
        task_idx = action % N_TASKS_MAX
        if device_idx >= len(DEVICE_IDS):
            return
        dev_id = DEVICE_IDS[device_idx]
        twin = self.dt.get(dev_id)
        if not twin or not twin.is_idle():
            return
        order = self.om.find_best_task(dev_id)
        if order:
            twin.assign_task(order)
            order.assigned_device = dev_id
            order.started_at = self.current_time

    def _get_metrics(self) -> dict:
        devices = {}
        for dev_id, twin in self.dt._twins.items():
            spindle = twin.shadow.latest_happy("spindle_speed")
            devices[f"{dev_id}_util"] = 1.0 if (spindle and spindle > 0) else 0.0
        return {
            **devices,
            "total_energy": self._compute_total_energy(),
            "time": self.current_time,
            "queue_depth": len(self.om.get_pending()),
            "completed": len(self.om.completed),
        }

    def _compute_total_energy(self) -> float:
        total = 0.0
        for dev_id, twin in self.dt._twins.items():
            power = twin.shadow.latest_happy("power_consumed")
            if power and power > 0:
                total += power * self.current_time / 3600
        return total
