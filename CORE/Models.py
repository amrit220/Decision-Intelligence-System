from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class Factors:
    importance: int   
    urgency: int      
    effort: int       
    reward: int       


@dataclass(frozen=True)
class Context:
    energy: int       
    mood: int
    #available_minutes = int 


@dataclass
class Option:
    option_id: str
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
