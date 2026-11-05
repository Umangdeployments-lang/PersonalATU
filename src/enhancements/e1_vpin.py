import numpy as np
from numba import jit

class E1VPIN:
    """
    E1: VPIN Order-Flow Toxicity - Detecting informed institutional dumping
    VPIN = Σ|V_buy - V_sell| / (n · V_τ)
    """
    @staticmethod
    @jit(nopython=True)
    def compute_vpin(buy_volumes: np.ndarray, sell_volumes: np.ndarray) -> float:
        n = len(buy_volumes)
        if n == 0:
            return 0.0
        v_tau = np.mean(buy_volumes + sell_volumes)
        if v_tau == 0:
            return 0.0
        return np.sum(np.abs(buy_volumes - sell_volumes)) / (n * v_tau)

    @staticmethod
    def check_enhancement(vpin: float) -> bool:
        return vpin < 0.75  # Block reversion fades if VPIN > 0.75