"""
CORE-01: TimescaleDB Hypertables, Redis 7 & Ring Buffers
Infrastructure provisioning and health checks.
"""
import asyncio
import asyncpg
import redis.asyncio as redis
from typing import Optional

class CoreInfrastructure:
    def __init__(self, dsn: str, redis_url: str):
        self.dsn = dsn
        self.redis_url = redis_url
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None

    async def initialize(self):
        self.db_pool = await asyncpg.create_pool(self.dsn, min_size=5, max_size=20)
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        await self._verify_schema()

    async def _verify_schema(self):
        async with self.db_pool.acquire() as conn:
            tables = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            required = {'market_ticks', 'footprint_bars', 'gex_snapshots', 'trade_executions', 'critic_evaluations'}
            found = {r['table_name'] for r in tables}
            missing = required - found
            if missing:
                raise RuntimeError(f"Missing tables: {missing}")

    async def health_check(self) -> bool:
        try:
            async with self.db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            await self.redis_client.ping()
            return True
        except Exception:
            return False

    async def close(self):
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            await self.redis_client.close()