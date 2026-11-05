import numpy as np
from numba import jit

class P4Footprint:
    """
    P4: Footprint Chart - Bid x Ask volume matrix with diagonal imbalance ratios
    """
    @staticmethod
    @jit(nopython=True)
    def diagonal_imbalance_ratio(ask_vol: np.ndarray, bid_vol: np.ndarray) -> float:
        if np.sum(bid_vol) == 0:
            return np.inf
        return np.sum(ask_vol) / np.sum(bid_vol)

    @staticmethod
    def check_pillar(ask_vol: np.ndarray, bid_vol: np.ndarray) -> bool:
        ratio = P4Footprint.diagonal_imbalance_ratio(ask_vol, bid_vol)
        return ratio >= 3.0  # 300% threshold