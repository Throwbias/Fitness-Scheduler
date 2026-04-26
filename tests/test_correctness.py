from src.algorithms.greedy_scheduler import build_greedy_plan
from src.algorithms.local_search import refine_plan_with_replacements
from src.utils.evaluator import evaluate_weekly_plan
from src.utils.loader import load_exercises, load_request


def test_local_search_does_not_decrease_score():
    exercises = load_exercises("data/exercises.json")
    request = load_request("data/sample_request.json")
    lookup = {ex.id: ex for ex in exercises}

    greedy_plan = build_greedy_plan(exercises, request)
    greedy_metrics = evaluate_weekly_plan(greedy_plan, request, lookup)

    refined_plan, refined_metrics = refine_plan_with_replacements(
        greedy_plan, exercises, request, dict(lookup)
    )

    assert refined_metrics["total_score"] >= greedy_metrics["total_score"]
