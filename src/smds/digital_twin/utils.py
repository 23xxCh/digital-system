from typing import Callable


def rk4_step(
    f: Callable[[float, list], list],
    t: float,
    y: list,
    dt: float,
) -> list:
    """Generic 4th-order Runge-Kutta stepper.

    Args:
        f: derivative function f(t, y) -> dy/dt (list)
        t: current time
        y: current state vector (list of floats)
        dt: time step

    Returns:
        y_next: state vector after one step of size dt
    """
    k1 = f(t, y)
    k2 = f(t + dt / 2, [y[i] + dt / 2 * k1[i] for i in range(len(y))])
    k3 = f(t + dt / 2, [y[i] + dt / 2 * k2[i] for i in range(len(y))])
    k4 = f(t + dt, [y[i] + dt * k3[i] for i in range(len(y))])
    return [
        y[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
        for i in range(len(y))
    ]
