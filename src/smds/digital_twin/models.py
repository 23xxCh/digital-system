from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional


class ShadowState(IntEnum):
    HAPPY = 0
    NIL = 1
    EMPTY = 2
    ERROR = 3


@dataclass
class DataPoint:
    timestamp: datetime
    value: Any
    shadow: ShadowState
    error_code: Optional[str] = None

    @classmethod
    def happy(cls, value: Any) -> DataPoint:
        return cls(datetime.now(), value, ShadowState.HAPPY)

    @classmethod
    def nil(cls) -> DataPoint:
        return cls(datetime.now(), None, ShadowState.NIL)

    @classmethod
    def empty(cls) -> DataPoint:
        return cls(datetime.now(), None, ShadowState.EMPTY)

    @classmethod
    def error(cls, code: str) -> DataPoint:
        return cls(datetime.now(), None, ShadowState.ERROR, code)


@dataclass
class DataShadow:
    device_id: str
    history: Dict[str, List[DataPoint]] = field(default_factory=dict)
    max_history: int = 1000
    _happy_cache: Dict[str, Any] = field(default_factory=dict, repr=False)
    on_shadow_transition: Optional[Callable[[str, ShadowState, ShadowState], None]] = field(
        default=None, repr=False
    )

    def record(self, key: str, dp: DataPoint):
        if key not in self.history:
            self.history[key] = []

        # Detect shadow transition before appending
        old_dp = self.history[key][-1] if self.history[key] else None
        old_shadow = old_dp.shadow if old_dp else None

        self.history[key].append(dp)
        if len(self.history[key]) > self.max_history:
            self.history[key] = self.history[key][-self.max_history:]

        # Update O(1) happy cache
        if dp.shadow == ShadowState.HAPPY:
            self._happy_cache[key] = dp.value

        # Fire transition callback
        if old_shadow is not None and dp.shadow != old_shadow and self.on_shadow_transition:
            self.on_shadow_transition(key, old_shadow, dp.shadow)

    def latest(self, key: str) -> Optional[DataPoint]:
        seq = self.history.get(key, [])
        return seq[-1] if seq else None

    def latest_happy(self, key: str) -> Optional[Any]:
        return self._happy_cache.get(key)
