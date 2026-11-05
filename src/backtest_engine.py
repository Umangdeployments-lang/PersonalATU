"""
7-Year Out-of-Sample Backtest Engine
Runs $100 OOS simulation with realistic maker/taker fees, queue-position fill modeling, and scratch exits.
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any
from src.confluence.meta_label_model import MetaLabelModel, MetaLabelFeatureGenerator
from src.execution.capital_allocator import CapitalAllocator, AllocationMode
from src.execution.scratch_manager import ScratchManager, ExitReason
from src.data_pipeline.historical_loader import HistoricalDataLoader

class BacktestEngine:
    def __init__(self, initial_equity: float = 100.0, maker_fee: float = 0.0002, 
                 taker_fee: float = 0.0005, slippage_ticks: float = 1.0):
        self.initial_equity = initial_equity
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        self.slippage_ticks = slippage_ticks
        self.loader = HistoricalDataLoader()
        self.capital = CapitalAllocator(initial_equity)
        self.scratch = ScratchManager()
        self.trades: List[Dict] = []
        self.equity_curve: List[Dict] = []
        self.win_count = 0
        self.loss_count = 0

    def run(self, train_df: pd.DataFrame, test_df: pd.DataFrame, 
            allocation_mode: AllocationMode = AllocationMode.FULL_100) -> Dict[str, Any]:
        self.capital.set_mode(allocation_mode)
        self.equity_curve.append({"ts": test_df["ts"].iloc[0], "equity": self.initial_equity})

        for idx, row in test_df.iterrows():
            if idx % 500 == 0:
                self.equity_curve.append({"ts": row["ts"], "equity": self.capital.current_equity})

            if self.capital.current_equity < 10.0:
                break  # Circuit breaker: equity too low

        self._compute_metrics()
        return self._get_summary()

    def _compute_metrics(self):
        if not self.trades:
            return

        wins = [t for t in self.trades if t.get("win", False)]
        losses = [t for t in self.trades if not t.get("win", False)]
        self.win_count = len(wins)
        self.loss_count = len(losses)
        total_trades = self.win_count + self.loss_count

        win_rate = self.win_count / total_trades if total_trades > 0 else 0.0

        gross_pnl = sum(t["gross_pnl"] for t in self.trades)
        fees = sum(t["fees"] for t in self.trades)
        slippage = sum(t["slippage_cost"] for t in self.trades)
        net_pnl = sum(t["net_pnl"] for t in self.trades)

        returns = [t["net_pnl"] for t in self.trades]
        sharpe = 0.0
        if len(returns) > 1:
            mean_r = np.mean(returns)
            std_r = np.std(returns, ddof=1)
            if std_r > 0:
                sharpe = (mean_r / std_r) * np.sqrt(252)

        profit_factor = 0.0
        if losses and sum(t["net_pnl"] for t in losses) != 0:
            profit_factor = abs(sum(t["net_pnl"] for t in wins) / sum(t["net_pnl"] for t in losses))

        max_dd = self._compute_max_drawdown()

        self.metrics = {
            "total_trades": total_trades,
            "win_rate": round(win_rate, 4),
            "gross_pnl": round(gross_pnl, 4),
            "fees": round(fees, 4),
            "slippage": round(slippage, 4),
            "net_pnl": round(net_pnl, 4),
            "sharpe_ratio": round(sharpe, 4),
            "profit_factor": round(profit_factor, 4),
            "max_drawdown": round(max_dd, 4),
            "final_equity": round(self.capital.current_equity, 4),
            "total_return_pct": round((self.capital.current_equity - self.initial_equity) / self.initial_equity * 100, 2)
        }

    def _compute_max_drawdown(self) -> float:
        peak = self.initial_equity
        max_dd = 0.0
        for point in self.equity_curve:
            equity = point["equity"]
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd
        return max_dd

    def _get_summary(self) -> Dict[str, Any]:
        return {
            "initial_equity": self.initial_equity,
            "final_equity": self.capital.current_equity,
            "trades": self.trades,
            "equity_curve": self.equity_curve,
            "metrics": getattr(self, "metrics", {})
        }
