import numpy as np
from numba import jit

class P2VolumeProfile:
    """
    P2: Volume Profile (VP) - Developing POC, VAH/VAL, HVN/LVN nodes
    """
    @staticmethod
    @jit(nopython=True)
    def compute_poc(volumes: np.ndarray, prices: np.ndarray) -> float:
        return prices[np.argmax(volumes)]

    @staticmethod
    @jit(nopython=True)
    def compute_vah_val(volumes: np.ndarray, prices: np.ndarray) -> tuple:
        total_vol = np.sum(volumes)
        cum_vol = 0.0
        target_vol = total_vol * 0.70
        vah_idx = val_idx = np.argmax(volumes)
        
        for i in range(len(volumes)):
            cum_vol += volumes[i]
            if cum_vol >= target_vol * 0.5:
                val_idx = i
                break
        for i in range(len(volumes) - 1, -1, -1):
            cum_vol += volumes[i]
            if cum_vol >= target_vol * 0.5:
                vah_idx = i
                break
        return prices[vah_idx], prices[val_idx]

    @staticmethod
    def check_pillar(price: float, poc: float, vah: float, val: float, hvn: np.ndarray, lvn: np.ndarray) -> bool:
        near_poc = abs(price - poc) / poc < 0.0015
        near_val = abs(price - val) / val < 0.0015
        near_vah = abs(price - vah) / vah < 0.0015
        return near_poc or near_val or near_vah