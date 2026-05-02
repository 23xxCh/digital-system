from smds.digital_twin.reward_calculator import RewardCalculator
from smds.digital_twin.order_manager import Order


def test_reward_throughput_part_a():
    calc = RewardCalculator()
    orders = [Order("O1", "PART-A", "OP10", "prog.nc", completed=True)]
    r = calc.compute({}, orders, {}, 0)
    assert r == 10.0


def test_reward_throughput_part_b():
    calc = RewardCalculator()
    orders = [Order("O1", "PART-B", "OP10", "prog.nc", completed=True)]
    r = calc.compute({}, orders, {}, 0)
    assert r == 8.0


def test_reward_balance_penalty():
    calc = RewardCalculator()
    metrics = {"CNC-001_util": 1.0, "CNC-002_util": 0.0, "CNC-003_util": 0.0}
    r = calc.compute(metrics, [], {}, 0)
    assert r < 0


def test_reward_delay_penalty():
    calc = RewardCalculator()
    order = Order("O1", "PART-A", "OP10", "prog.nc", due_time=100.0)
    r = calc.compute({}, [order], {"time": 200.0}, 200.0)
    assert r < 0


def test_reward_no_double_count():
    calc = RewardCalculator()
    order = Order("O1", "PART-A", "OP10", "prog.nc", completed=True, _rewarded=True)
    r = calc.compute({}, [order], {}, 0)
    assert r == 0.0
