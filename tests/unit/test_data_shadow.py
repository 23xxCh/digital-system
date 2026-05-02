from smds.digital_twin.models import DataPoint, DataShadow, ShadowState


def test_shadow_record_and_retrieve():
    shadow = DataShadow("TEST-001")
    dp = DataPoint.happy(42.0)
    shadow.record("temperature", dp)
    assert shadow.latest("temperature").value == 42.0
    assert shadow.latest("temperature").shadow == ShadowState.HAPPY


def test_shadow_empty_history_returns_none():
    shadow = DataShadow("TEST-001")
    assert shadow.latest("nonexistent") is None


def test_shadow_history_cap():
    shadow = DataShadow("TEST-001", max_history=5)
    for i in range(10):
        shadow.record("temp", DataPoint.happy(float(i)))
    assert len(shadow.history["temp"]) == 5
    assert shadow.latest("temp").value == 9.0


def test_shadow_latest_happy_skips_non_happy():
    shadow = DataShadow("TEST-001")
    shadow.record("speed", DataPoint.happy(100.0))
    shadow.record("speed", DataPoint.nil())
    shadow.record("speed", DataPoint.error("FAULT"))
    assert shadow.latest_happy("speed") == 100.0


def test_shadow_latest_happy_all_non_happy():
    shadow = DataShadow("TEST-001")
    shadow.record("speed", DataPoint.nil())
    shadow.record("speed", DataPoint.error("FAULT"))
    assert shadow.latest_happy("speed") is None
