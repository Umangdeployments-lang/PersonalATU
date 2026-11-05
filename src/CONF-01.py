"""
CONF-01: Triple-Check Confluence Engine & LightGBM Meta-Filter
Re-export for module naming consistency.
"""
from src.confluence.triple_check_engine import TripleCheckEngine, PillarCheckResult

__all__ = ["TripleCheckEngine", "PillarCheckResult"]