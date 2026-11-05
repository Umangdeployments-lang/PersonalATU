class E2LPSR:
    """
    E2: Anti-Spoofing LPSR Filter
    LPSR = (ΔQ_add − ΔQ_cancel) / (ΔQ_exec + ε)
    Rejects wall if cancel rate > 35%
    """
    @staticmethod
    def compute_lpsr(delta_q_add: float, delta_q_cancel: float, delta_q_exec: float) -> float:
        eps = 1e-10
        return (delta_q_add - delta_q_cancel) / (delta_q_exec + eps)

    @staticmethod
    def check_enhancement(lpsr: float, cancel_rate: float) -> bool:
        return cancel_rate <= 0.35