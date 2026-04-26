import json
from pathlib import Path
from typing import List

from src.data_structures.models import Exercise, PlanningRequest


def load_exercises(path: str | Path) -> List[Exercise]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Exercise(**item) for item in raw]


def load_request(path: str | Path) -> PlanningRequest:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return PlanningRequest(**raw)
