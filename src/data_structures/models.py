from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Exercise:
    """
    The fundamental unit of the system. Represents a single movement 
    loaded from the SQL database with all associated physiological metadata.
    """
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
    """
    The 'Goal State' for the algorithm. Encapsulates all user-defined 
    constraints and preferences used to calculate the fitness score.
    """
    days_available: List[int]  # Calendar indices: 0 (Mon) to 6 (Sun)
    session_time_limit: int
    goal: str
    required_categories: List[str]
    daily_fatigue_cap: int
    max_exercises_per_session: int
    desired_training_days_per_week: int

@dataclass
class Individual:
    """
    Represents a candidate workout plan (a member of the GA population).
    The 'chromosome' is a 7-slot list mapping to days of the week.
    """
    # Chromosome structure: List[Day[List[Exercises]]]
    chromosome: List[List[Exercise]] = field(default_factory=lambda: [[] for _ in range(7)])
    fitness_score: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)

    def get_active_days(self) -> List[int]:
        """Returns indices of days that currently contain exercises."""
        return [i for i, day in enumerate(self.chromosome) if len(day) > 0]