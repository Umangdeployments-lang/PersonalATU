"""
CORE-02: Automated Critic Gate Engine (critic_gate.py)
Re-export for module naming consistency.
"""
from src.critic.critic_gate import CriticGateAuditor, EvaluationResult, assert_production_unlocked

__all__ = ["CriticGateAuditor", "EvaluationResult", "assert_production_unlocked"]