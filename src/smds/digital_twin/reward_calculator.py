from __future__ import annotations

from typing import Dict, List, Optional

from .configs import RewardConfig
from .order_manager import Order


class RewardCalculator:
    def __init__(self, config: Optional[RewardConfig] = None):
        self.config = config or RewardConfig()

    def compute(
        self,
        metrics: Dict,
        orders: List[Order],
        prev_metrics: Dict,
        current_time: float,
    ) -> float:
        r = 0.0

        # Throughput reward
        for order in orders:
            if order.completed and not order._rewarded:
                if order.part_type == "PART-A":
                    r += self.config.throughput_part_a
                else:
                    r += self.config.throughput_part_b
                order._rewarded = True

        # Balance penalty (CNC utilization imbalance)
        cnc_utils = [
            metrics.get(f"CNC-{i:03d}_util", 0)
            for i in range(1, 4)
        ]
        imbalance = abs(max(cnc_utils) - min(cnc_utils))
        r -= imbalance * self.config.balance_penalty_weight

        # Energy penalty
        delta_energy = metrics.get("total_energy", 0) - prev_metrics.get("total_energy", 0)
        r -= delta_energy * self.config.energy_penalty_weight

        # Delay penalty
        for order in orders:
            if order.due_time and current_time > order.due_time and not order.completed:
                delay_min = (current_time - order.due_time) / 60.0
                r -= delay_min * self.config.delay_penalty_rate

        return r
