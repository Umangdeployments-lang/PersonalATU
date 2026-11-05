import numpy as np
from numba import jit

class P5Heatmap:
    """
    P5: Liquidity Heatmaps - Resting limit order density and age
    """
    @staticmethod
    @jit(nopython=True)
    def is_wall_persistent(order_age_sec: float, cancel_rate: float) -> bool:
        return order_age_sec > 180.0 and cancel_rate < 0.25

    @staticmethod
    def check_pillar(depth_percentile: float, order_age_sec: float, cancel_rate: float) -> bool:
        return depth_percentile >= 0.90 and P5Heatmap.is_wall_persistent(order_age_sec, cancel_rate)