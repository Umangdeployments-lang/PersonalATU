import numpy as np
from numba import jit

class P6BigTrades:
    """
    P6: Big Trades (Block & Sweep) - Microsecond trade-ID sequencing
    """
    @staticmethod
    @jit(nopython=True)
    def is_block_sweep(trade_size: float, rolling_99th_percentile: float) -> bool:
        return trade_size >= rolling_99th_percentile

    @staticmethod
    def check_pillar(trade_size: float, rolling_99th_percentile: float) -> bool:
        return P6BigTrades.is_block_sweep(trade_size, rolling_99th_percentile)