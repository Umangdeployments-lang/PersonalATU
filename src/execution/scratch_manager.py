import time
import threading
from dataclasses import dataclass
from enum import Enum

class ExitReason(Enum):
    TARGET_HIT = "TARGET_HIT"
    SCRATCH_ABSORPTION_FAIL = "SCRATCH_ABSORPTION_FAIL"
    TRAIL_STOP = "TRAIL_STOP"
    STRUCTURAL_STOP = "STRUCTURAL_STOP"

@dataclass
class ScratchExitConfig:
    min_scratch_ms: int = 500
    max_scratch_ms: int = 1500
    max_tick_loss: int = 1

class ScratchManager:
    """
    Active Order-Flow Micro-Invalidation Scratch Exit
    Monitors T+500ms to T+10s: if absorption fails or wall pulls, fires instant Scratch Exit (0 to -1 tick)
    """
    def __init__(self, config: ScratchExitConfig = None):
        self.config = config or ScratchExitConfig()
        self.position_active = False
        self.entry_time = None
        self.entry_price = None
        self.direction = None  # LONG or SHORT
        self.scratch_triggered = False
        self._lock = threading.Lock()

    def on_entry(self, price: float, direction: str):
        with self._lock:
            self.position_active = True
            self.entry_time = time.time() * 1000  # ms
            self.entry_price = price
            self.direction = direction
            self.scratch_triggered = False

    def on_exit(self):
        with self._lock:
            self.position_active = False
            self.entry_time = None
            self.entry_price = None
            self.direction = None
            self.scratch_triggered = False

    def check_scratch_conditions(self, current_price: float, heatmap_wall_pulled: bool, gex_flip: bool, 
                                  daily_dd_breached: bool) -> tuple:
        """
        Returns (should_exit, exit_reason)
        """
        if not self.position_active or self.scratch_triggered:
            return (False, None)

        elapsed_ms = (time.time() * 1000) - self.entry_time

        if daily_dd_breached:
            self.scratch_triggered = True
            return (True, ExitReason.STRUCTURAL_STOP)

        if gex_flip:
            self.scratch_triggered = True
            return (True, ExitReason.STRUCTURAL_STOP)

        if heatmap_wall_pulled:
            self.scratch_triggered = True
            return (True, ExitReason.SCRATCH_ABSORPTION_FAIL)

        if elapsed_ms >= self.config.max_scratch_ms:
            tick_diff = abs(current_price - self.entry_price)
            if tick_diff <= self.config.max_tick_loss:
                self.scratch_triggered = True
                return (True, ExitReason.SCRATCH_ABSORPTION_FAIL)

        return (False, None)