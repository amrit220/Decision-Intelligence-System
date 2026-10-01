from dataclasses import dataclass

@dataclass
class Option:
    name: str
    importance: float
    effort: float
    urgency: float
    reward: float

@dataclass
class Factors:
    name: str
    weight: float

@dataclass
class Decision:
    options: list[Option]
    factors: list[Factors]

@dataclass
class Outcome:
    option: Option
    score: float