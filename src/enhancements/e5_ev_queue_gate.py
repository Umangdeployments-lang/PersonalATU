class E5EVQueueGate:
    """
    E5: Queue-Position & Fee EV Gate
    Expected Target ≥ 3.0 × (Maker/Taker Fee + Slippage)
    """
    @staticmethod
    def compute_ev(target_ticks: float, fee_ticks: float, slippage_ticks: float) -> float:
        round_trip = 2 * fee_ticks + slippage_ticks
        if round_trip == 0:
            return np.inf
        return target_ticks / round_trip

    @staticmethod
    def check_enhancement(target_ticks: float, fee_ticks: float, slippage_ticks: float) -> bool:
        ev = E5EVQueueGate.compute_ev(target_ticks, fee_ticks, slippage_ticks)
        return ev >= 3.0