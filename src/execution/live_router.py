import logging
from src.critic.critic_gate import assert_production_unlocked, CriticGateAuditor

logger = logging.getLogger("live_router")

class LiveOrderRouter:
    """
    Execution Router - Critic-Locked Order Routing
    Verifies Critic Score >= 9.0 before every order submission.
    Routes Post-Only Maker / IOC Taker orders.
    """
    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.critic_auditor = CriticGateAuditor()

    def submit_order(self, symbol: str, side: str, order_type: str, 
                     quantity: float, price: float = None, 
                     time_in_force: str = "GTC") -> dict:
        """
        Submits order after verifying production is unlocked.
        """
        assert_production_unlocked()
        
        if self.testnet:
            logger.info(f"[TESTNET] Submitting {side} {symbol} {order_type} qty={quantity} price={price}")
            return {
                "order_id": f"testnet_{int(__import__('time').time()*1000)}",
                "status": "NEW",
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
                "price": price
            }
        else:
            logger.warning("LIVE ORDER ROUTING NOT YET IMPLEMENTED - Testnet mode enforced")
            raise RuntimeError("Live routing locked until all modules score >= 9.0")

    def cancel_all_orders(self, symbol: str) -> bool:
        logger.info(f"Cancelling all orders for {symbol}")
        return True