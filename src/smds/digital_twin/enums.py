from enum import IntEnum


class CNCState(IntEnum):
    IDLE = 0
    RUN = 1
    PAUSE = 2
    ALARM = 3
    MAINT = 4


class RobotState(IntEnum):
    IDLE = 0
    MOVE = 1
    GRIP = 2
    WELD = 3
    ALARM = 4
    TEACH = 5


class AGVState(IntEnum):
    IDLE = 0
    MOVE = 1
    LOAD = 2
    UNLOAD = 3
    CHARGE = 4
    ALARM = 5


class WarehouseState(IntEnum):
    NORMAL = 0
    FULL = 1
    MAINT = 2
    ALARM = 3
