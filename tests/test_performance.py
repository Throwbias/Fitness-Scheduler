import time

import pytest

from src.algorithms.greedy_scheduler import build_greedy_plan
from src.algorithms.local_search import refine_plan_with_replacements
from src.utils.loader import load_exercises, load_request


def test_greedy_scheduler_runtime():
    """Ensure the constructive greedy algorithm executes in under 0.1 seconds."""
    exercises = load_exercises("data/exercises_large.json")
    request = load_request("data/sample_request.json")

    start_time = time.time()
    plan = build_greedy_plan(exercises, request)
    execution_time = time.time() - start_time

    assert (
        execution_time < 0.1
    ), f"Greedy Scheduler is too slow: {execution_time:.4f} seconds"


def test_local_search_runtime():
    """Ensure the local search refinement completes in under 2.0 seconds."""
    exercises = load_exercises("data/exercises_large.json")
    request = load_request("data/sample_request.json")
    exercise_lookup = {ex.id: ex for ex in exercises}

    # We need a base plan to refine
    greedy_plan = build_greedy_plan(exercises, request)

    start_time = time.time()
    refined_plan, metrics = refine_plan_with_replacements(
        greedy_plan, exercises, request, exercise_lookup, max_iterations=50
    )
    execution_time = time.time() - start_time

    assert (
        execution_time < 2.0
    ), f"Local Search is too slow: {execution_time:.4f} seconds"
