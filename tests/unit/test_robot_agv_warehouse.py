from smds.digital_twin.robot_twin import RobotTwin
from smds.digital_twin.agv_twin import AGVTwin
from smds.digital_twin.warehouse_twin import WarehouseTwin
from smds.digital_twin.enums import RobotState, AGVState, WarehouseState


def test_robot_simulate_idle():
    rob = RobotTwin("ROB-001", "ns=2;s=ROB-001")
    out = rob.simulate(1.0)
    assert out["tcp_speed"] == 0.0
    assert out["grip_state"] is False


def test_robot_joint_limit_validation():
    rob = RobotTwin("ROB-001", "ns=2;s=ROB-001")
    result = rob.sync_from_physical({"joint_angles": [200, 0, 0, 0, 0, 0]})
    assert result is False


def test_agv_battery_drain():
    agv = AGVTwin("AGV-001", "ns=2;s=AGV-001")
    agv._state = AGVState.MOVE
    initial = agv.battery
    agv.simulate(100.0)
    assert agv.battery < initial


def test_agv_needs_charge():
    agv = AGVTwin("AGV-001", "ns=2;s=AGV-001")
    agv.battery = 15.0
    assert agv.needs_charge() is True


def test_warehouse_store_and_retrieve():
    wh = WarehouseTwin()
    wh.store_request("PART-A", quantity=5)
    wh.task_queue[0]["duration"] = 0.05
    wh.simulate(0.1)
    assert wh.part_a_stock == 5
    wh.retrieve_request("PART-A", quantity=2)
    wh.task_queue[0]["duration"] = 0.05
    wh.simulate(0.1)
    assert wh.part_a_stock == 3


def test_warehouse_full_state():
    wh = WarehouseTwin()
    wh.part_a_stock = 191
    wh.simulate(0.1)
    assert wh._state == WarehouseState.FULL
