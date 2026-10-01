from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class Factors:
    importance: int   # 1-10
    urgency: int      # 1-10
    effort: int       # 1-10
    reward: int       # 1-10


@dataclass(frozen=True)
class Context:
    energy: int       # 1-10


@dataclass
class Option:
    option_name: str
    label: str
    factors: Factors


@dataclass(frozen=True)
class ScoringPolicy:
    w_imp: float
    w_urg: float
    w_rew: float
    w_eff: float
    energy_sensitivity: float
    mode_name: str


@dataclass
class ScoreBreakdown:
    option_id: str
    raw: float
    score: float
    contributions: Dict[str, float]
    effort_weight_applied: float