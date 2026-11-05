import numpy as np
from numba import jit

class P1OrderFlow:
    """
    P1: Order Flow (L2/L3 DOM) - Replenishment Velocity vs Depletion Rate
    """
    @staticmethod
    @jit(nopython=True)
    def replenishment_ratio(bid_replenish: np.ndarray, ask_depletion: np.ndarray) -> float:
        if np.sum(ask_depletion) == 0:
            return np.inf
        return np.sum(bid_replenish) / np.sum(ask_depletion)

    @staticmethod
    def check_pillar(lob_depth: np.ndarray) -> bool:
        if len(lob_depth) < 20:
            return False
        bid_replenish = np.diff(lob_depth[:, 0])
        ask_depletion = np.diff(lob_depth[:, 1])
        ratio = P1OrderFlow.replenishment_ratio(bid_replenish, ask_depletion)
        return ratio >= 1.8