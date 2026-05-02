from smds.digital_twin.cnc_twin import CNCTwin
from smds.digital_twin.robot_twin import RobotTwin
from smds.digital_twin.agv_twin import AGVTwin
from smds.digital_twin.warehouse_twin import WarehouseTwin
from smds.digital_twin.manager import DigitalTwinManager


def register_all_twins(manager: DigitalTwinManager):
    manager.register(CNCTwin("CNC-001", "ns=2;s=CNC-001"))
    manager.register(CNCTwin("CNC-002", "ns=2;s=CNC-002"))
    manager.register(CNCTwin("CNC-003", "ns=2;s=CNC-003"))
    manager.register(RobotTwin("ROB-001", "ns=2;s=ROB-001"))
    manager.register(RobotTwin("ROB-002", "ns=2;s=ROB-002"))
    manager.register(AGVTwin("AGV-001", "ns=2;s=AGV-001"))
    manager.register(WarehouseTwin("WH-001", "ns=2;s=WH-001"))


def test_sim_to_prod_no_state_loss():
    manager = DigitalTwinManager()
    register_all_twins(manager)
    manager.set_mode("simulation")
    manager.simulate_all(10.0)
    sim_report = manager.all_health_reports()
    manager.set_mode("production")
    prod_report = manager.all_health_reports()
    assert set(sim_report.keys()) == set(prod_report.keys())


def test_verify_consistency_catches_drift():
    manager = DigitalTwinManager()
    sim_data = {"CNC-001": {"spindle_speed": 8000}}
    real_data = {"CNC-001": {"spindle_speed": 5000}}
    discrepancies = manager.verify_consistency(sim_data, real_data)
    assert len(discrepancies) == 1
    assert "CNC-001.spindle_speed" in discrepancies[0]
