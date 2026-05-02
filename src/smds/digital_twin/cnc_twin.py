from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from .base import DigitalTwinBase
from .configs import CNCConfig
from .enums import CNCState
from .exceptions import SimulationError
from .models import DataPoint
from .utils import rk4_step


@dataclass
class CNCPhysicsParams:
    spindle_inertia: float = 0.12
    spindle_damping: float = 0.008
    cutting_force_coeff: float = 0.15
    thermal_capacity: float = 8500.0
    thermal_resistance: float = 0.025
    vibration_stiffness: float = 2.4e6
    vibration_damping: float = 1200.0

    def to_vector(self) -> np.ndarray:
        return np.array([
            self.spindle_inertia, self.spindle_damping, self.cutting_force_coeff,
            self.thermal_capacity, self.thermal_resistance,
            self.vibration_stiffness, self.vibration_damping,
        ])

    @classmethod
    def from_vector(cls, vec: np.ndarray) -> CNCPhysicsParams:
        return cls(*vec)


class CNCTwin(DigitalTwinBase):
    # Physical constants (nominal values from DMG Mori CMX 600)
    SPINDLE_INERTIA = 0.12       # J: kg·m²
    SPINDLE_DAMPING = 0.008      # b: Nm/(rad/s)
    MOTOR_TORQUE_MAX = 35.0      # τ_max: Nm
    CUTTING_FORCE_COEFF = 0.15   # K_c: Nm/rpm
    THERMAL_CAPACITY = 8500.0    # C: J/K
    THERMAL_RESISTANCE = 0.025   # R: K/W
    AMBIENT_TEMP = 22.0          # T_amb: °C
    MOTOR_EFFICIENCY = 0.88      # η
    VIBRATION_MASS = 2.5         # m: kg
    VIBRATION_STIFFNESS = 2.4e6  # k: N/m
    VIBRATION_DAMPING = 1200.0   # c: N·s/m
    TOOL_WEAR_RATE = 0.02        # μm/s
    TOOL_CRITICAL_WEAR = 150.0   # μm

    def __init__(
        self,
        device_id: str = "CNC-001",
        opcua_node_id: str = "ns=2;s=CNC-001",
        config: Optional[CNCConfig] = None,
    ):
        super().__init__(device_id, opcua_node_id)
        self.config = config or CNCConfig()
        self._omega: float = 0.0
        self._temperature: float = self.AMBIENT_TEMP
        self._tool_wear: float = 0.0
        self._vib_x: float = 0.0
        self._vib_vx: float = 0.0
        self.tool_life: List[float] = [100.0] * self.config.tool_count
        self.current_program: Optional[str] = None
        self.part_count_today: int = 0
        self.reject_count_today: int = 0

    def _initial_state(self) -> CNCState:
        return CNCState.IDLE

    def _validate_hardware_state(self, raw: Dict[str, Any]) -> bool:
        spindle = raw.get("spindle_speed")
        if spindle is not None and (spindle < 0 or spindle > self.config.max_spindle_speed * 1.1):
            return False
        temp = raw.get("temperature")
        if temp is not None and (temp > 85.0 or temp < -10.0):
            return False
        vibration = raw.get("vibration_x")
        if vibration is not None and vibration > self.config.vibration_critical * 2:
            return False
        return True

    def _on_sync_success(self, raw_data: Dict[str, Any]):
        active_tool = raw_data.get("active_tool")
        cycle_time = raw_data.get("cycle_time")
        if active_tool is not None and cycle_time is not None:
            idx = active_tool - 1
            if 0 <= idx < len(self.tool_life):
                self.tool_life[idx] -= cycle_time / 60.0
        new_state = raw_data.get("machine_state")
        if new_state is not None:
            self._state = CNCState(new_state)

    def simulate(self, delta_t: float) -> Dict[str, Any]:
        dt = min(delta_t, self.config.ode_substep)
        n_steps = max(1, int(delta_t / dt))
        target_omega = self._target_speed_rpm() * 2 * math.pi / 60

        for _ in range(n_steps):
            state_vec = [self._omega, self._temperature, self._vib_x, self._vib_vx, self._tool_wear]

            def deriv(t, y):
                omega, temp, vib_x, vib_vx, wear = y
                tau_motor = self._motor_torque(target_omega, omega)
                tau_cut = self._cutting_torque(omega) if self._state == CNCState.RUN else 0.0
                tau_friction = self.SPINDLE_DAMPING * omega
                d_omega = (tau_motor - tau_cut - tau_friction) / self.SPINDLE_INERTIA

                if self._state == CNCState.RUN:
                    q_gen = tau_motor * omega * (1 - self.MOTOR_EFFICIENCY)
                else:
                    q_gen = 0.0
                q_dissipate = (temp - self.AMBIENT_TEMP) / self.THERMAL_RESISTANCE
                d_temp = (q_gen - q_dissipate) / self.THERMAL_CAPACITY

                f_cut = (tau_cut * 50) if self._state == CNCState.RUN else 0.0
                d_vib_x = vib_vx
                d_vib_vx = (f_cut - self.VIBRATION_DAMPING * vib_vx - self.VIBRATION_STIFFNESS * vib_x) / self.VIBRATION_MASS

                if self._state == CNCState.RUN and tau_cut > 0:
                    d_wear = self.TOOL_WEAR_RATE * (tau_cut / self.MOTOR_TORQUE_MAX)
                else:
                    d_wear = 0.0

                return [d_omega, d_temp, d_vib_x, d_vib_vx, d_wear]

            new_state = rk4_step(deriv, 0.0, state_vec, dt)
            self._omega = max(0, min(new_state[0], target_omega * 1.05))
            self._temperature = new_state[1]
            self._vib_x = new_state[2]
            self._vib_vx = new_state[3]
            self._tool_wear = max(0, new_state[4])

        # Update tool life
        if self.tool_life:
            self.tool_life[0] = max(0, 100 * (1 - self._tool_wear / self.TOOL_CRITICAL_WEAR))

        return self._build_output()

    def _motor_torque(self, target_omega: float, current_omega: float) -> float:
        error = target_omega - current_omega
        torque = error * 0.5
        return max(-self.MOTOR_TORQUE_MAX, min(self.MOTOR_TORQUE_MAX, torque))

    def _cutting_torque(self, omega: float) -> float:
        if self.current_program is None:
            return 0.0
        rpm = omega * 60 / (2 * math.pi)
        return self.CUTTING_FORCE_COEFF * rpm * (1 + self._tool_wear / self.TOOL_CRITICAL_WEAR)

    def _target_speed_rpm(self) -> float:
        return 8000.0 if self._state == CNCState.RUN else 0.0

    def _build_output(self) -> Dict[str, Any]:
        rpm = self._omega * 60 / (2 * math.pi)
        tau_motor = self._motor_torque(0, self._omega)
        power = max(0, tau_motor * self._omega / 1000)
        return {
            "machine_state": self._state.value,
            "spindle_speed": round(rpm),
            "spindle_load": round(abs(tau_motor) / self.MOTOR_TORQUE_MAX * 100, 1) if self._state == CNCState.RUN else 0,
            "feed_rate": 500 if self._state == CNCState.RUN else 0,
            "temperature": round(self._temperature, 1),
            "vibration_x": round(abs(self._vib_x) * 10, 2),
            "vibration_y": round(abs(self._vib_x) * 7, 2),
            "vibration_z": round(abs(self._vib_x) * 5, 2),
            "power_consumed": round(power, 1),
            "coolant_flow": 15.0 if self._state == CNCState.RUN else 0.0,
            "cycle_time": 0.05,
        }

    # ---------- Polymorphic dispatch ----------

    def is_idle(self) -> bool:
        return self._state == CNCState.IDLE

    def can_accept_task(self, task_type: str) -> bool:
        return self.is_idle() and task_type in ("PART-A", "PART-B")

    def assign_task(self, order) -> None:
        self.start_program(order.program, order.part_type)

    # ---------- Public methods ----------

    def start_program(self, program: str, part_type: str) -> str:
        if self._state == CNCState.ALARM:
            raise SimulationError(f"Cannot start: {self.device_id} in ALARM state")
        self.current_program = program
        self._state = CNCState.RUN
        return f"JOB-{self.device_id}-{datetime.now():%Y%m%d%H%M%S}"

    def emergency_stop(self):
        self._state = CNCState.ALARM
        self.current_program = None
        self.shadow.record("emergency_stop", DataPoint.happy(datetime.now().isoformat()))

    def tool_change_needed(self) -> List[int]:
        return [i + 1 for i, life in enumerate(self.tool_life) if life < 10.0]


class CalibrationEngine:
    def __init__(self, twin: CNCTwin):
        self.twin = twin
        self.nominal = CNCPhysicsParams()

    def calibrate(self, real_runs: List[Dict]) -> CNCPhysicsParams:
        from scipy.optimize import least_squares

        def objective(param_vec):
            params = CNCPhysicsParams.from_vector(param_vec)
            self._apply_params(params)
            total_error = 0.0
            for run in real_runs:
                sim_output = self._simulate_run(run)
                for key, weight in [("spindle_speed", 1.0), ("temperature", 0.5), ("vibration_x", 0.3)]:
                    if key in sim_output and key in run.get("data", {}):
                        diff = np.mean([abs(s - r) for s, r in zip(sim_output[key], run["data"][key])])
                        total_error += weight * diff
            return total_error

        x0 = self.nominal.to_vector()
        bounds = (x0 * 0.5, x0 * 2.0)
        result = least_squares(objective, x0, bounds=bounds, max_nfev=500)
        return CNCPhysicsParams.from_vector(result.x)

    def _apply_params(self, params: CNCPhysicsParams):
        self.twin.SPINDLE_INERTIA = params.spindle_inertia
        self.twin.SPINDLE_DAMPING = params.spindle_damping
        self.twin.CUTTING_FORCE_COEFF = params.cutting_force_coeff
        self.twin.THERMAL_CAPACITY = params.thermal_capacity
        self.twin.THERMAL_RESISTANCE = params.thermal_resistance
        self.twin.VIBRATION_STIFFNESS = params.vibration_stiffness
        self.twin.VIBRATION_DAMPING = params.vibration_damping

    def _simulate_run(self, run: Dict) -> Dict[str, List[float]]:
        self.twin._state = CNCState.IDLE
        self.twin._omega = 0.0
        self.twin._temperature = self.twin.AMBIENT_TEMP
        output: Dict[str, List[float]] = {"spindle_speed": [], "temperature": [], "vibration_x": []}
        for event in run.get("events", []):
            if event["type"] == "START":
                self.twin._state = CNCState.RUN
                self.twin.current_program = event.get("program")
            elif event["type"] == "STOP":
                self.twin._state = CNCState.IDLE
            sim_data = self.twin.simulate(event.get("duration", 1.0))
            output["spindle_speed"].append(sim_data["spindle_speed"])
            output["temperature"].append(sim_data["temperature"])
            output["vibration_x"].append(sim_data["vibration_x"])
        return output

    def check_drift(self, sim_val: float, real_val: float, key: str) -> bool:
        if real_val == 0:
            return abs(sim_val) < 0.1
        return abs(sim_val - real_val) / abs(real_val) < 0.20
