from smds.digital_twin.order_manager import Order


def test_order_default_values():
    o = Order("O1", "PART-A", "OP10", "prog.nc")
    assert o.completed is False
    assert o._rewarded is False
    assert o.assigned_device is None


def test_order_tuple_unpacking():
    o = Order("O1", "PART-A", "OP10", "prog.nc", target_pose=(100.0, 200.0, 300.0, 0, 0, 0))
    assert len(o.target_pose) == 6
