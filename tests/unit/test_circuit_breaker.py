import time

from smds.digital_twin.opcua_connector import CircuitBreaker, CircuitBreakerState


def test_circuit_breaker_closed_normal():
    cb = CircuitBreaker(failure_threshold=3, timeout=5.0)
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.allow_request() is True


def test_circuit_breaker_opens_after_n_failures():
    cb = CircuitBreaker(failure_threshold=3, timeout=5.0)
    for _ in range(3):
        cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    assert cb.allow_request() is False


def test_circuit_breaker_half_open_after_timeout():
    cb = CircuitBreaker(failure_threshold=3, timeout=0.1)
    for _ in range(3):
        cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    time.sleep(0.15)
    assert cb.state == CircuitBreakerState.HALF_OPEN
    assert cb.allow_request() is True


def test_circuit_breaker_resets_on_success():
    cb = CircuitBreaker(failure_threshold=3, timeout=0.1)
    for _ in range(3):
        cb.record_failure()
    time.sleep(0.15)
    cb.allow_request()  # -> HALF_OPEN
    cb.record_success()
    assert cb.state == CircuitBreakerState.CLOSED


def test_circuit_breaker_reopens_on_half_open_failure():
    cb = CircuitBreaker(failure_threshold=3, timeout=0.1)
    for _ in range(3):
        cb.record_failure()
    time.sleep(0.15)
    cb.allow_request()  # -> HALF_OPEN
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
