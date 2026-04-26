from src.algorithms.greedy_scheduler import build_greedy_plan
from src.algorithms.random_scheduler import build_random_plan
from src.utils.loader import load_exercises, load_request


def test_greedy_scheduler_runs():
    exercises = load_exercises("data/exercises.json")
    request = load_request("data/sample_request.json")

    plan = build_greedy_plan(exercises, request)

    assert len(plan.sessions) == len(request.days_available)

    for session in plan.sessions.values():
        assert session.total_time <= request.session_time_limit
        assert session.total_fatigue <= request.daily_fatigue_cap


def test_random_scheduler_runs():
    exercises = load_exercises("data/exercises.json")
    request = load_request("data/sample_request.json")

    plan = build_random_plan(exercises, request, seed=42)

    assert len(plan.sessions) == len(request.days_available)

    for session in plan.sessions.values():
        assert session.total_time <= request.session_time_limit
        assert session.total_fatigue <= request.daily_fatigue_cap
