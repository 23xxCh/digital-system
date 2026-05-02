from smds.digital_twin.cnc_twin import CNCTwin
from smds.digital_twin.models import ShadowState


def test_sync_happy_path():
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    result = twin.sync_from_physical({"spindle_speed": 8000, "temperature": 42.0})
    assert result is True
    assert twin.shadow.latest("spindle_speed").shadow == ShadowState.HAPPY
    assert twin.shadow.latest("spindle_speed").value == 8000


def test_sync_nil_values():
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    twin.sync_from_physical({"spindle_speed": None})
    assert twin.shadow.latest("spindle_speed").shadow == ShadowState.NIL


def test_sync_empty_containers():
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    twin.sync_from_physical({"alarms": []})
    assert twin.shadow.latest("alarms").shadow == ShadowState.EMPTY


def test_sync_out_of_range_values():
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    # Use a generic sensor key (no hardware validation) to test SENSOR_OUT_OF_RANGE
    twin.sync_from_physical({"pressure": -950})
    assert twin.shadow.latest("pressure").shadow == ShadowState.ERROR
    assert "SENSOR_OUT_OF_RANGE" in twin.shadow.latest("pressure").error_code


def test_sync_validation_failure():
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    result = twin.sync_from_physical({"spindle_speed": 50000})
    assert result is False
    assert twin.shadow.latest("sync_status").shadow == ShadowState.ERROR


def test_shadow_transition_callback():
    transitions = []
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    twin.shadow.on_shadow_transition = lambda key, old, new: transitions.append((key, old, new))
    twin.sync_from_physical({"spindle_speed": 8000})
    twin.sync_from_physical({"spindle_speed": None})
    assert len(transitions) == 1
    assert transitions[0] == ("spindle_speed", ShadowState.HAPPY, ShadowState.NIL)
