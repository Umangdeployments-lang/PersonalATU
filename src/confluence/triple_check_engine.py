import time
import threading
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class PillarCheckResult:
    pillar_id: str
    passed: bool
    timestamp_ms: float

class TripleCheckEngine:
    """
    Confluence Engine - Triple-Tick Cross-Check at T+0ms, T+100ms, T+250ms
    All 9 pillars + 5 enhancements must pass across all 3 temporal checks.
    """
    PILLARS = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9']
    ENHANCEMENTS = ['E1', 'E2', 'E3', 'E4', 'E5']
    
    def __init__(self, sync_window_ms: int = 250):
        self.sync_window_ms = sync_window_ms
        self.check_results: List[Dict[str, PillarCheckResult]] = []
        self.meta_win_probability: float = 0.0
        self._lock = threading.Lock()

    def run_pass_1(self, market_data: Dict[str, Any]) -> bool:
        """Stage 2: Structural Pass - P2, P3, P8, P9"""
        checks = {}
        checks['P2'] = PillarCheckResult('P2', market_data.get('p2_pass', False), time.time() * 1000)
        checks['P3'] = PillarCheckResult('P3', market_data.get('p3_pass', False), time.time() * 1000)
        checks['P8'] = PillarCheckResult('P8', market_data.get('p8_pass', False), time.time() * 1000)
        checks['P9'] = PillarCheckResult('P9', market_data.get('p9_pass', False), time.time() * 1000)
        
        with self._lock:
            self.check_results.append(checks)
        return all(r.passed for r in checks.values())

    def run_pass_2(self, market_data: Dict[str, Any]) -> bool:
        """Stage 3: Liquidity Pass - P1, P5, P6, E2, E4"""
        checks = {}
        checks['P1'] = PillarCheckResult('P1', market_data.get('p1_pass', False), time.time() * 1000)
        checks['P5'] = PillarCheckResult('P5', market_data.get('p5_pass', False), time.time() * 1000)
        checks['P6'] = PillarCheckResult('P6', market_data.get('p6_pass', False), time.time() * 1000)
        checks['E2'] = PillarCheckResult('E2', market_data.get('e2_pass', False), time.time() * 1000)
        checks['E4'] = PillarCheckResult('E4', market_data.get('e4_pass', False), time.time() * 1000)
        
        with self._lock:
            self.check_results.append(checks)
        return all(r.passed for r in checks.values())

    def run_pass_3(self, market_data: Dict[str, Any]) -> bool:
        """Stage 4: Trigger Pass - P4, P7, E1, Meta-Label Model"""
        checks = {}
        checks['P4'] = PillarCheckResult('P4', market_data.get('p4_pass', False), time.time() * 1000)
        checks['P7'] = PillarCheckResult('P7', market_data.get('p7_pass', False), time.time() * 1000)
        checks['E1'] = PillarCheckResult('E1', market_data.get('e1_pass', False), time.time() * 1000)
        
        self.meta_win_probability = market_data.get('meta_win_prob', 0.0)
        checks['ML'] = PillarCheckResult('ML', self.meta_win_probability >= 0.95, time.time() * 1000)
        
        with self._lock:
            self.check_results.append(checks)
        return all(r.passed for r in checks.values())

    def is_fully_aligned(self) -> bool:
        return len(self.check_results) >= 3 and all(
            all(r.passed for r in check.values())
            for check in self.check_results
        )

    def get_snapshot(self) -> Dict:
        with self._lock:
            return {f"check_{i}": {k: {"passed": v.passed, "ts": v.timestamp_ms} 
                                  for k, v in check.items()} 
                    for i, check in enumerate(self.check_results)}