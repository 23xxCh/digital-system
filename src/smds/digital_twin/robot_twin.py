from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import DigitalTwinBase
from .configs import RobotConfig
from .enums import RobotState


class RobotTwin(DigitalTwinBase):
    def __init__(
        self,
        device_id: str = "ROB-001",
        opcua_node_id: str = "ns=2;s=ROB-001",
        config: Optional[RobotConfig] = None,
    ):
        super().__init__(device_id, opcua_node_id)
        self.config = config or RobotConfig()
        self.joint_angles: List[float] = [0.0] * 6
        self.tcp_position: List[float] = [0.0, 0.0, 0.0]
        self.tcp_orientation: List[float] = [0.0, 0.0, 0.0]
        self.grip_state: bool = False
        self.speed_override: float = 100.0

    def _initial_state(self) -> RobotState:
        return RobotState.IDLE

    def _validate_hardware_state(self, raw: Dict[str, Any]) -> bool:
        angles = raw.get("joint_angles")
        if angles and len(angles) == 6:
            for i, (a, (lo, hi)) in enumerate(zip(angles, self.config.joint_limits)):
                if a < lo - 5 or a > hi + 5:
                    return False
        return True

    def _on_sync_success(self, raw_data: Dict[str, Any]):
        if "joint_angles" in raw_data:
            self.joint_angles = raw_data["joint_angles"]
        if "tcp_x" in raw_data:
            self.tcp_position = [
                raw_data.get("tcp_x", 0),
                raw_data.get("tcp_y", 0),
                raw_data.get("tcp_z", 0),
            ]

    def simulate(self, delta_t: float) -> Dict[str, Any]:
        import random
        if self._state == RobotState.MOVE:
            jitter = [random.uniform(-0.1, 0.1) for _ in range(6)]
            angles = [a + j for a, j in zip(self.joint_angles, jitter)]
        else:
            angles = list(self.joint_angles)

        torques = [abs(ang) * 0.5 + 2.0 + random.uniform(0, 0.5) for ang in angles]
        return {
            "robot_state": self._state.value,
            "joint_angles": [round(a, 4) for a in angles],
            "joint_torques": [round(t, 2) for t in torques],
            "joint_temps": [round(35 + t * 0.5, 1) for t in torques],
            "tcp_x": round(self.tcp_position[0], 3),
            "tcp_y": round(self.tcp_position[1], 3),
            "tcp_z": round(self.tcp_position[2], 3),
            "tcp_rx": self.tcp_orientation[0],
            "tcp_ry": self.tcp_orientation[1],
            "tcp_rz": self.tcp_orientation[2],
            "tcp_speed": 200.0 if self._state == RobotState.MOVE else 0.0,
            "grip_state": self.grip_state,
            "grip_force": 50.0 if self.grip_state else 0.0,
        }

    # ---------- Polymorphic dispatch ----------

    def is_idle(self) -> bool:
        return self._state in (RobotState.IDLE, RobotState.GRIP)

    def can_accept_task(self, task_type: str) -> bool:
        return self.is_idle() and task_type in ("LOAD", "UNLOAD")

    def assign_task(self, order) -> None:
        if order.target_pose:
            self.move_to(*order.target_pose, speed=200)

    # ---------- Public methods ----------

    def move_to(self, x, y, z, rx=0, ry=0, rz=0, speed=200.0):
        self.tcp_position = [x, y, z]
        self.tcp_orientation = [rx, ry, rz]
        self.speed_override = speed
        self._state = RobotState.MOVE

    def grip(self, force: float = 50.0):
        self.grip_state = True
        self._state = RobotState.GRIP

    def release(self):
        self.grip_state = False
        self._state = RobotState.IDLE
