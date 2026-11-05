import numpy as np
from enum import Enum

class AllocationMode(Enum):
    FULL_100 = "FULL_100"
    HALF_50 = "HALF_50"
    KELLY_25 = "KELLY_25"

class CapitalAllocator:
    """
    $100 Capital Allocation Modes:
    - FULL_100: 100% equity as margin, risk 1.5% standard / 2.5% 10/10 confluence
    - HALF_50: 50% locked reserve, 50% active margin
    - KELLY_25: Quarter-Kelly compounder f* = 0.25 * ((p*b - q) / b)
    """
    def __init__(self, initial_equity: float = 100.0):
        self.initial_equity = initial_equity
        self.current_equity = initial_equity
        self.mode = AllocationMode.FULL_100
        self.trade_history = []

    def set_mode(self, mode: AllocationMode):
        self.mode = mode

    def compute_position_size(self, stop_distance_ticks: float, confluence_score: float, is_10_of_10: bool = False) -> float:
        risk_pct = 0.025 if is_10_of_10 else 0.015
        
        if self.mode == AllocationMode.FULL_100:
            risk_capital = self.current_equity * risk_pct
        elif self.mode == AllocationMode.HALF_50:
            risk_capital = (self.current_equity * 0.5) * risk_pct
        elif self.mode == AllocationMode.KELLY_25:
            p = self._get_win_rate()
            b = self._get_payoff_ratio()
            if b == 0:
                kelly_f = 0.0
            else:
                kelly_f = 0.25 * ((p * b - (1 - p)) / b)
            risk_capital = self.current_equity * max(0.0, min(kelly_f, 0.5)) * risk_pct
        else:
            risk_capital = self.current_equity * risk_pct

        if stop_distance_ticks <= 0:
            return 0.0
        return risk_capital / stop_distance_ticks

    def _get_win_rate(self) -> float:
        if len(self.trade_history) < 20:
            return 0.55
        recent = self.trade_history[-100:]
        return sum(1 for t in recent if t.get('win', False)) / len(recent)

    def _get_payoff_ratio(self) -> float:
        if len(self.trade_history) < 20:
            return 2.0
        recent = self.trade_history[-100:]
        wins = [t['pnl'] for t in recent if t.get('win', False)]
        losses = [abs(t['pnl']) for t in recent if not t.get('win', False)]
        if not losses or not wins:
            return 2.0
        return np.mean(wins) / np.mean(losses)

    def update_equity(self, net_pnl: float, win: bool):
        self.current_equity += net_pnl
        self.trade_history.append({'pnl': net_pnl, 'win': win})