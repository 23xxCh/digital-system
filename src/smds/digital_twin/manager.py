from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import DigitalTwinBase
from .exceptions import DigitalTwinError
from .opcua_connector import OPCUAConnector


class DigitalTwinManager:
    def __init__(self):
        self._twins: Dict[str, DigitalTwinBase] = {}
        self.mode: str = "simulation"
        self._opcua_connector: Optional[OPCUAConnector] = None

    def register(self, twin: DigitalTwinBase):
        self._twins[twin.device_id] = twin

    def get(self, device_id: str) -> Optional[DigitalTwinBase]:
        return self._twins.get(device_id)

    def set_mode(self, mode: str):
        if mode not in ("simulation", "production"):
            raise ValueError(f"Unknown mode: {mode}")
        self.mode = mode

    def sync_all(self, data_source: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        results = {}
        for device_id, raw_data in data_source.items():
            twin = self._twins.get(device_id)
            if twin:
                results[device_id] = twin.sync_from_physical(raw_data)
            else:
                results[device_id] = False
        return results

    def simulate_all(self, delta_t: float) -> Dict[str, Dict[str, Any]]:
        return {dev_id: twin.simulate(delta_t) for dev_id, twin in self._twins.items()}

    def step_all(self, delta_t: float) -> Dict[str, Dict[str, Any]]:
        if self.mode == "production":
            if not self._opcua_connector:
                raise DigitalTwinError("OPC UA connector not initialized in production mode")
            raise DigitalTwinError("Production mode requires async — use sync_all with external data")
        return self.simulate_all(delta_t)

    def all_health_reports(self) -> Dict[str, Dict[str, Any]]:
        return {dev_id: twin.health_report() for dev_id, twin in self._twins.items()}

    def verify_consistency(self, sim_data: dict, real_data: dict) -> List[str]:
        discrepancies = []
        for dev_id in sim_data:
            if dev_id in real_data:
                for key in sim_data[dev_id]:
                    sim_val = sim_data[dev_id].get(key)
                    real_val = real_data[dev_id].get(key)
                    if sim_val is not None and real_val is not None:
                        if isinstance(sim_val, (int, float)) and isinstance(real_val, (int, float)):
                            if abs(sim_val - real_val) > abs(real_val) * 0.2:
                                discrepancies.append(
                                    f"{dev_id}.{key}: sim={sim_val:.2f}, real={real_val:.2f}"
                                )
        return discrepancies

    # ---------- Polymorphic dispatch helpers ----------

    def get_idle_devices(self) -> List[str]:
        return [dev_id for dev_id, twin in self._twins.items() if twin.is_idle()]

    def get_capable_devices(self, task_type: str) -> List[str]:
        return [dev_id for dev_id, twin in self._twins.items() if twin.can_accept_task(task_type)]
