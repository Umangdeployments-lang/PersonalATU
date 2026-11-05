import numpy as np
from numba import jit

class P8VWAPSuite:
    """
    P8: VWAP Suite - Session, Anchored, ±1..3σ Bands
    """
    @staticmethod
    @jit(nopython=True)
    def compute_vwap(prices: np.ndarray, volumes: np.ndarray) -> float:
        total_vol = np.sum(volumes)
        if total_vol == 0:
            return prices[-1] if len(prices) > 0 else 0.0
        return np.sum(prices * volumes) / total_vol

    @staticmethod
    @jit(nopython=True)
    def compute_std_bands(prices: np.ndarray, volumes: np.ndarray, vwap: float) -> tuple:
        total_vol = np.sum(volumes)
        if total_vol == 0:
            return vwap, vwap, vwap
        variance = np.sum(volumes * ((prices - vwap) ** 2)) / total_vol
        std = np.sqrt(variance)
        return vwap + 1.0 * std, vwap + 2.0 * std, vwap + 3.0 * std

    @staticmethod
    def check_pillar(price: float, vwap: float, band_std2: float, band_std3: float) -> bool:
        return price <= band_std2 or price <= band_std3