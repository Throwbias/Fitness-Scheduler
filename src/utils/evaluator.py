import statistics
from src.data_structures.models import Exercise, PlanningRequest, WeeklyPlan

# ... (Keep compute_coverage_score, compute_priority_score, etc. as they are) ...

def count_constraint_violations(
    plan: WeeklyPlan, request: PlanningRequest, exercise_lookup: dict[str, Exercise]
) -> int:
    violations = 0
    exercise_last_seen = {}  # Tracks the last day_index an exercise was performed
    
    # Sort days to ensure we check recovery chronologically
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    sorted_days = sorted(plan.sessions.keys(), key=lambda d: day_order.index(d))

    for day_idx, day_name in enumerate(sorted_days):
        session = plan.sessions[day_name]
        if not session.exercise_ids:
            continue

        # 1. Hard Constraints: Time, Fatigue, and Volume
        if session.total_time > request.session_time_limit:
            violations += 1
        if session.total_fatigue > request.daily_fatigue_cap:
            violations += 1
        if len(session.exercise_ids) > request.max_exercises_per_session:
            violations += 1

        # 2. Bio-Constraint: Heavy Lifts per Session
        # We define "Heavy" as any exercise requiring 2+ days of recovery
        heavy_count = sum(1 for ex_id in session.exercise_ids 
                         if exercise_lookup[ex_id].min_recovery_days >= 2)
        if heavy_count > request.max_heavy_exercises_per_session:
            violations += 1

        # 3. Bio-Constraint: Recovery Windows
        for ex_id in session.exercise_ids:
            if ex_id in exercise_last_seen:
                days_since = day_idx - exercise_last_seen[ex_id]
                required = exercise_lookup[ex_id].min_recovery_days
                if days_since < required:
                    violations += 1
            exercise_last_seen[ex_id] = day_idx

    return violations

def evaluate_weekly_plan(
    plan: WeeklyPlan,
    request: PlanningRequest,
    exercise_lookup: dict[str, Exercise],
) -> dict:
    # ... (Scores remain the same) ...
    
    # Update this call to pass exercise_lookup
    constraint_violations = count_constraint_violations(plan, request, exercise_lookup)

    total_score = (
        coverage_score * 25
        + priority_score * 20
        + time_utilization_score * 15
        + fatigue_balance_score * 15
        + training_frequency_score * 15
        - constraint_violations * 20  # Increased penalty for violating bio-constraints
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