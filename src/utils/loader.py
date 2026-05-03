import json
from pathlib import Path
from typing import List, Union
import logging
from src.data_structures.models import Exercise, PlanningRequest

def load_request(path: Union[str, Path]) -> PlanningRequest:
    """
    Parses the user's JSON request file.
    Includes a 'Cleaning Layer' to convert string-based day names 
    (e.g., 'Monday') into the integer indices used by the GA chromosome.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        if "days_available" in raw:
            raw["days_available"] = [
                day_map[d.lower()] if isinstance(d, str) else d 
                for d in raw["days_available"]
            ]

        # Use __annotations__ to dynamically filter for only valid PlanningRequest keys
        allowed_keys = PlanningRequest.__annotations__.keys()
        filtered_raw = {k: v for k, v in raw.items() if k in allowed_keys}
        
        return PlanningRequest(**filtered_raw)
        
    except Exception as e:
        logging.error(f"Critical error loading request: {e}")
        # Fail-safe: Return a basic 3-day full-body request
        return PlanningRequest([0, 2, 4], 60, "General", [], 30, 5, 3)