import numpy as np
from numba import jit

class P3NetGEX:
    """
    P3: Net Gamma Exposure (GEX) - Dealer gamma positioning
    GEXK = (ΓcallOIcall − ΓputOIput) × M × S² × 0.01
    """
    @staticmethod
    @jit(nopython=True)
    def compute_net_gex(gamma_call_oi: float, gamma_put_oi: float, M: float, S: float) -> float:
        return (gamma_call_oi - gamma_put_oi) * M * (S ** 2) * 0.01

    @staticmethod
    @jit(nopython=True)
    def find_zero_gamma_flip(strikes: np.array, gex_values: np.array, spot: float) -> float:
        for i in range(len(strikes) - 1):
            if (gex_values[i] <= 0 and gex_values[i+1] > 0) or (gex_values[i] >= 0 and gex_values[i+1] < 0):
                return strikes[i]
        return spot

    @staticmethod
    def check_pillar(gex: float, regime: str) -> bool:
        if regime == "POSITIVE_GAMMA":
            return True  # Fade extremes toward POC/VWAP
        elif regime == "NEGATIVE_GAMMA":
            return True  # Trade momentum breakouts
        return False