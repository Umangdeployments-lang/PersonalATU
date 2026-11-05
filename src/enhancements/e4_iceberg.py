class E4Iceberg:
    """
    E4: Passive Iceberg Detector
    Fires when V_exec ≥ 3.5 × Q_vis without tick depletion
    """
    @staticmethod
    def check_enhancement(v_exec: float, q_vis: float) -> bool:
        if q_vis == 0:
            return False
        return v_exec >= 3.5 * q_vis