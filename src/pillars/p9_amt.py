class P9AuctionMarketTheory:
    """
    P9: Auction Market Theory (AMT) - Balance vs Imbalance, 80% Rule
    """
    @staticmethod
    def check_pillar(price_outside_va: bool, reentry_count: int, value_area_width: float) -> bool:
        if price_outside_va and reentry_count >= 1:
            return True
        return False