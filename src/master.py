"""
MASTER: Aggregate System Readiness & 7Y OOS $100 Backtest
Orchestrates the full AEGIS-9 pipeline.
"""
from src.core_infrastructure import CoreInfrastructure
from src.critic_engine import CriticGateAuditor, assert_production_unlocked
from src.data_loader import HistoricalDataLoader, BinanceWebSocketIngestor
from src.confluence_engine import TripleCheckEngine
from src.confluence.meta_label_model import MetaLabelModel, MetaLabelFeatureGenerator
from src.execution_engine import CapitalAllocator, ScratchManager, LiveOrderRouter
from src.ui_engine import flask_app, update_dashboard
from src.pillars import (
    P1OrderFlow, P2VolumeProfile, P3NetGEX, P4Footprint,
    P5Heatmap, P6BigTrades, P7DeltaCVD, P8VWAPSuite, P9AuctionMarketTheory
)
from src.enhancements import E1VPIN, E2LPSR, E3VannaCharm, E4Iceberg, E5EVQueueGate
from src.backtest_engine import BacktestEngine

class Aegis9Master:
    def __init__(self, dsn: str, redis_url: str, initial_equity: float = 100.0):
        self.infra = CoreInfrastructure(dsn, redis_url)
        self.critic = CriticGateAuditor()
        self.loader = HistoricalDataLoader()
        self.ingestor = BinanceWebSocketIngestor()
        self.confluence = TripleCheckEngine()
        self.capital = CapitalAllocator(initial_equity)
        self.scratch = ScratchManager()
        self.router = LiveOrderRouter(testnet=True)
        self.meta_model = MetaLabelModel()
        self.backtest = BacktestEngine(initial_equity)
        self.pillars = {
            "P1": P1OrderFlow(), "P2": P2VolumeProfile(), "P3": P3NetGEX(),
            "P4": P4Footprint(), "P5": P5Heatmap(), "P6": P6BigTrades(),
            "P7": P7DeltaCVD(), "P8": P8VWAPSuite(), "P9": P9AuctionMarketTheory()
        }
        self.enhancements = {
            "E1": E1VPIN(), "E2": E2LPSR(), "E3": E3VannaCharm(),
            "E4": E4Iceberg(), "E5": E5EVQueueGate()
        }

    async def initialize(self):
        await self.infra.initialize()
        passed, results = self.critic.audit_all(strict_min_score=9.0)
        if not passed:
            failed = [k for k, v in results.items() if not v.passed_9_gate]
            raise RuntimeError(f"System not ready for production. Failed modules: {failed}")
        print("AEGIS-9 MASTER: All systems UNLOCKED for production")

    async def run_backtest(self, train_df, test_df, mode="FULL_100"):
        from src.execution.capital_allocator import AllocationMode
        alloc_mode = AllocationMode[mode]
        return self.backtest.run(train_df, test_df, alloc_mode)

    async def shutdown(self):
        await self.infra.close()

__all__ = ["Aegis9Master"]
