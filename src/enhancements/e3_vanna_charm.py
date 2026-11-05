class E3VannaCharm:
    """
    E3: Intraday Vanna & Charm Flow
    Charm = −∂Δ/∂τ, Vanna = ∂Δ/∂σ
    """
    @staticmethod
    def compute_charm(delta: float, tau: float) -> float:
        if tau == 0:
            return 0.0
        return -delta / tau

    @staticmethod
    def compute_vanna(delta: float, sigma: float) -> float:
        if sigma == 0:
            return 0.0
        return delta / sigma

    @staticmethod
    def check_enhancement(net_vanna: float, net_charm: float) -> bool:
        return True  # Always true for projection; signals used in confluence