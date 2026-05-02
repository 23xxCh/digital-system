from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class CNCConfig:
    max_spindle_speed: int = 12000
    max_feed_rate: int = 20000
    tool_count: int = 30
    max_power: float = 22.0
    normal_temp_range: Tuple[float, float] = (15.0, 65.0)
    vibration_warn: float = 7.0
    vibration_critical: float = 12.0
    ode_substep: float = 0.05  # 50ms, per engineering review #9


@dataclass
class RobotConfig:
    joint_limits: List[Tuple[float, float]] = field(default_factory=lambda: [
        (-180, 180), (-130, 130), (-230, 65),
        (-190, 190), (-120, 120), (-360, 360),
    ])
    max_tcp_speed: float = 2000.0  # mm/s
    grip_force_range: Tuple[float, float] = (0.0, 100.0)  # N


@dataclass
class AGVConfig:
    max_speed: float = 1500.0  # mm/s
    battery_capacity: float = 100.0  # %
    drain_rate: float = 0.002  # % per second while moving
    charge_threshold: float = 20.0  # % below which charging is needed


@dataclass
class RewardConfig:
    throughput_part_a: float = 10.0
    throughput_part_b: float = 8.0
    balance_penalty_weight: float = 0.5
    energy_penalty_weight: float = 0.8
    delay_penalty_rate: float = 0.1  # per minute overdue
