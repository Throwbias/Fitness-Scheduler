from dataclasses import dataclass, field
from typing import List, Dict


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
    equipment: List[str] = field(default_factory=list)
    goal_tags: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)


@dataclass
class PlanningRequest:
    days_available: List[str]
    session_time_limit: int
    goal: str
    required_categories: List[str]
    daily_fatigue_cap: int
    equipment_available: List[str] = field(default_factory=list)
    excluded_exercises: List[str] = field(default_factory=list)
    preferred_exercises: List[str] = field(default_factory=list)
    max_exercises_per_session: int = 4
    max_training_days_per_week: int = 5
    desired_training_days_per_week: int = 5
    min_start_score: float = 11.0
    min_continue_score: float = 5.5
    max_heavy_exercises_per_session: int = 2
    min_exercises_per_session: int = 2
    min_session_time_for_training_day: int = 15
    session_fullness_preference: str = "moderate"


@dataclass
class SessionPlan:
    day: str
    exercise_ids: List[str] = field(default_factory=list)
    total_time: int = 0
    total_fatigue: int = 0
    categories_hit: List[str] = field(default_factory=list)


@dataclass
class WeeklyPlan:
    sessions: Dict[str, SessionPlan]
    total_score: float = 0.0
    constraint_violations: int = 0