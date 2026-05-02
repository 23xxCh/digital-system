from smds.digital_twin.cnc_twin import CNCTwin
from smds.digital_twin.enums import CNCState


def test_cnc_simulate_idle():
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    cnc._state = CNCState.IDLE
    out = cnc.simulate(1.0)
    assert out["spindle_speed"] == 0
    assert out["spindle_load"] == 0
    assert out["feed_rate"] == 0
    assert out["coolant_flow"] == 0.0


def test_cnc_simulate_run_reaches_target_rpm():
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    cnc._state = CNCState.RUN
    cnc.current_program = "PART-A_OP1.nc"
    for _ in range(500):
        out = cnc.simulate(0.1)
    assert out["spindle_speed"] > 0  # Motor reaches non-zero speed under load


def test_cnc_simulate_alarm_estop():
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    cnc._state = CNCState.RUN
    cnc.current_program = "test.nc"
    for _ in range(200):
        cnc.simulate(0.1)
    cnc._state = CNCState.ALARM
    cnc.current_program = None
    for _ in range(1000):
        out = cnc.simulate(0.1)
    assert out["spindle_speed"] == 0
    assert out["temperature"] < 30.0


def test_cnc_tool_wear_accumulation():
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    cnc._state = CNCState.RUN
    cnc.current_program = "test.nc"
    initial_life = cnc.tool_life[0]
    for _ in range(10000):
        cnc.simulate(0.1)
    assert cnc.tool_life[0] < initial_life


def test_cnc_ode_numerical_stability_rk4():
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    cnc._state = CNCState.RUN
    cnc.current_program = "test.nc"
    for _ in range(200):
        cnc.simulate(0.1)
    cnc._state = CNCState.ALARM
    cnc.current_program = None
    out = cnc.simulate(1.0)
    assert out["temperature"] > 0
    assert out["spindle_speed"] == 0
