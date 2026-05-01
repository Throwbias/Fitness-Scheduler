import json
from pathlib import Path
from typing import List
import logging

from src.data_structures.models import Exercise, PlanningRequest

def load_exercises(path: str | Path) -> List[Exercise]:
    """
    Loads raw exercise data from a JSON file.
    Note: In production, we primarily use db_connector.py to fetch from SQL.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Exercise(**item) for item in raw]
    except Exception as e:
        logging.error(f"Failed to load exercises from {path}: {e}")
        return []

def load_request(path: str | Path) -> PlanningRequest:
    """
    Loads the user's planning constraints. 
    Includes a filter to match JSON keys to the PlanningRequest dataclass.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        
        # Mapping logic: Convert day names to integers if they exist as strings
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        if "days_available" in raw:
            processed_days = []
            for day in raw["days_available"]:
                if isinstance(day, str):
                    processed_days.append(day_map[day.lower()])
                else:
                    processed_days.append(day)
            raw["days_available"] = processed_days

        # Robustness: Only pass keys that exist in the PlanningRequest dataclass
        # This prevents 'TypeError: __init__() got an unexpected keyword argument'
        allowed_keys = PlanningRequest.__annotations__.keys()
        filtered_raw = {k: v for k, v in raw.items() if k in allowed_keys}
        
        return PlanningRequest(**filtered_raw)
        
    except Exception as e:
        logging.error(f"Failed to load request from {path}: {e}")
        # Return a safe default request if loading fails
        return PlanningRequest([0, 2, 4], 60, "General", [], 30, 5, 3)