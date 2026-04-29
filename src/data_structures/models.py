from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random

@dataclass
class Exercise:
    id: str
    name: str
    category: str
    muscle_group: str
    difficulty: str
    duration_min: int
    fatigue_cost: int
    priority: int
    min_recovery_days: int
    goal_tags: List[str]

@dataclass
class PlanningRequest:
    days_available: List[int]  # Now indices 0-6 (e.g., [0, 2, 4])
    session_time_limit: int
    goal: str
    required_categories: List[str]
    daily_fatigue_cap: int
    max_exercises_per_session: int
    desired_training_days_per_week: int # Used to guide the GA

@dataclass
class Individual:
    # The Chromosome: A list of 7 lists, each containing Exercise objects
    chromosome: List[List[Exercise]] = field(default_factory=lambda: [[] for _ in range(7)])
    fitness_score: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)

    def get_active_days(self) -> List[int]:
        return [i for i, day in enumerate(self.chromosome) if len(day) > 0]