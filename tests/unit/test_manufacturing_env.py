from smds.digital_twin.cnc_twin import CNCTwin
from smds.digital_twin.robot_twin import RobotTwin
from smds.digital_twin.agv_twin import AGVTwin
from smds.digital_twin.warehouse_twin import WarehouseTwin
from smds.digital_twin.manager import DigitalTwinManager
from smds.digital_twin.manufacturing_env import ManufacturingEnv
from smds.digital_twin.order_manager import OrderManager


def make_test_env(orders=None):
    dt = DigitalTwinManager()
    dt.register(CNCTwin("CNC-001", "ns=2;s=CNC-001"))
    dt.register(CNCTwin("CNC-002", "ns=2;s=CNC-002"))
    dt.register(CNCTwin("CNC-003", "ns=2;s=CNC-003"))
    dt.register(RobotTwin("ROB-001", "ns=2;s=ROB-001"))
    dt.register(RobotTwin("ROB-002", "ns=2;s=ROB-002"))
    dt.register(AGVTwin("AGV-001", "ns=2;s=AGV-001"))
    dt.register(WarehouseTwin("WH-001", "ns=2;s=WH-001"))
    om = OrderManager()
    if orders:
        om.orders = orders
    return ManufacturingEnv(dt, om)


def test_factorized_action_dispatch():
    env = make_test_env()
    obs = env.reset()
    assert obs.shape[0] == 67
    action = 0 * 20 + 0  # CNC-001 + first task
    obs, reward, done, info = env.step(action)
    assert info["step"] == 1


def test_action_no_idle_device():
    from smds.digital_twin.enums import CNCState
    env = make_test_env()
    env.reset()
    for dev_id in ["CNC-001", "CNC-002", "CNC-003"]:
        env.dt.get(dev_id)._state = CNCState.RUN
    obs, reward, done, info = env.step(0)
    assert info["step"] == 1


def test_done_on_all_completed():
    env = make_test_env(orders=[])
    obs = env.reset()
    env.om.completed = list(env.om.orders)
    obs, reward, done, info = env.step(6 * 20 + 0)  # WAIT-like action
    assert done is True


def test_done_on_max_steps():
    env = make_test_env()
    env.reset()
    env._step_count = 1000
    obs, reward, done, info = env.step(6 * 20 + 0)
    assert done is True
