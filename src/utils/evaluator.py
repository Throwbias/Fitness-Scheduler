import statistics

from src.data_structures.models import Exercise, PlanningRequest, WeeklyPlan


def compute_coverage_score(
    plan: WeeklyPlan, request: PlanningRequest, exercise_lookup: dict[str, Exercise]
) -> float:
    categories_hit = set()

    for session in plan.sessions.values():
        for ex_id in session.exercise_ids:
            categories_hit.add(exercise_lookup[ex_id].category)

    required = set(request.required_categories)
    if not required:
        return 1.0

    return len(categories_hit & required) / len(required)


def compute_priority_score(
    plan: WeeklyPlan, exercise_lookup: dict[str, Exercise]
) -> float:
    all_selected = [
        exercise_lookup[ex_id]
        for session in plan.sessions.values()
        for ex_id in session.exercise_ids
    ]

    if not all_selected:
        return 0.0

    total_priority = sum(ex.priority for ex in all_selected)
    max_possible = len(all_selected) * 10  # assumes priority scale tops out at 10

    return total_priority / max_possible if max_possible else 0.0


def compute_time_utilization_score(plan: WeeklyPlan, request: PlanningRequest) -> float:
    active_sessions = [
        session for session in plan.sessions.values() if len(session.exercise_ids) > 0
    ]

    if not active_sessions:
        return 0.0

    total_used = sum(session.total_time for session in active_sessions)
    total_available = len(active_sessions) * request.session_time_limit

    return total_used / total_available if total_available else 0.0


def compute_fatigue_balance_score(plan: WeeklyPlan) -> float:
    active_fatigue = [
        session.total_fatigue
        for session in plan.sessions.values()
        if len(session.exercise_ids) > 0
    ]

    if len(active_fatigue) <= 1:
        return 1.0

    variance = statistics.pvariance(active_fatigue)
    return 1 / (1 + variance)


def compute_training_frequency_score(
    plan: WeeklyPlan, request: PlanningRequest
) -> float:
    active_days = sum(
        1 for session in plan.sessions.values() if len(session.exercise_ids) > 0
    )

    target = request.desired_training_days_per_week

    if target <= 0:
        return 1.0

    return max(0.0, 1 - abs(active_days - target) / target)


def count_constraint_violations(plan: WeeklyPlan, request: PlanningRequest) -> int:
    violations = 0

    for session in plan.sessions.values():
        if session.total_time > request.session_time_limit:
            violations += 1
        if session.total_fatigue > request.daily_fatigue_cap:
            violations += 1
        if len(session.exercise_ids) > request.max_exercises_per_session:
            violations += 1

    return violations


def evaluate_weekly_plan(
    plan: WeeklyPlan,
    request: PlanningRequest,
    exercise_lookup: dict[str, Exercise],
) -> dict:
    coverage_score = compute_coverage_score(plan, request, exercise_lookup)
    priority_score = compute_priority_score(plan, exercise_lookup)
    time_utilization_score = compute_time_utilization_score(plan, request)
    fatigue_balance_score = compute_fatigue_balance_score(plan)
    training_frequency_score = compute_training_frequency_score(plan, request)
    constraint_violations = count_constraint_violations(plan, request)

    total_score = (
        coverage_score * 25
        + priority_score * 20
        + time_utilization_score * 15
        + fatigue_balance_score * 15
        + training_frequency_score * 15
        - constraint_violations * 10
    )

    return {
        "coverage_score": coverage_score,
        "priority_score": priority_score,
        "time_utilization_score": time_utilization_score,
        "fatigue_balance_score": fatigue_balance_score,
        "training_frequency_score": training_frequency_score,
        "constraint_violations": constraint_violations,
        "total_score": total_score,
    }
