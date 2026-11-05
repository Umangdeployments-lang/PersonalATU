import numpy as np
from numba import jit

class P7DeltaCVD:
    """
    P7: Delta & Cumulative Volume Delta (CVD) Absorption & Divergence
    """
    @staticmethod
    @jit(nopython=True)
    def compute_bar_delta(v_ask: float, v_bid: float) -> float:
        return v_ask - v_bid

    @staticmethod
    def check_pillar(cvd_divergence: bool, delta_flip: bool) -> bool:
        return cvd_divergence and delta_flip