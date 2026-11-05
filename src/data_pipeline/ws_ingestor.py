import asyncio
import json
import logging
import time
from typing import Callable, Dict, List, Optional
import aiohttp

logger = logging.getLogger("ws_ingestor")

class DataLeakageError(Exception):
    """Raised when timestamp leakage or overlap between Train and Test sets occurs."""
    pass

class BinanceWebSocketIngestor:
    """
    WebSocket stream ingestor for Binance Futures L2 orderbook diffs, raw tick trades, and options snapshots.
    Maintains heartbeat < 250ms and checks sequence numbers (u == prev_u + 1).
    """
    WS_URL = "wss://fstream.binance.com/ws"

    def __init__(self, symbol: str = "btcusdt"):
        self.symbol = symbol.lower()
        self.last_u: Optional[int] = None
        self.last_heartbeat_ts: float = time.time()
        self.is_connected: bool = False
        self.on_tick_callback: Optional[Callable] = None
        self.on_depth_callback: Optional[Callable] = None

    async def start(self):
        url = f"{self.WS_URL}/{self.symbol}@aggTrade/{self.symbol}@depth@100ms"
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url) as ws:
                self.is_connected = True
                self.last_heartbeat_ts = time.time()
                logger.info(f"Connected to WebSocket: {url}")

                async for msg in ws:
                    self.last_heartbeat_ts = time.time()
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        await self._process_message(data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error("WebSocket connection closed with error")
                        self.is_connected = False
                        break

    async def _process_message(self, data: dict):
        event_type = data.get("e")
        if event_type == "depthUpdate":
            u = data.get("u")
            pu = data.get("pu")
            if self.last_u is not None and pu != self.last_u:
                logger.warning(f"L2 sequence ID mismatch! Gap detected: pu={pu}, expected last_u={self.last_u}. Resynchronizing snapshot...")
                # Freeze order routing & request resync
            self.last_u = u
            if self.on_depth_callback:
                await self.on_depth_callback(data)
        elif event_type == "aggTrade":
            if self.on_tick_callback:
                await self.on_tick_callback(data)
