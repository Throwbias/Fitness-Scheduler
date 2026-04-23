from src.data_structures.models import Exercise, PlanningRequest, SessionPlan


def equipment_is_available(exercise: Exercise, request: PlanningRequest) -> bool:
    return all(eq in request.equipment_available for eq in exercise.equipment)


def is_excluded(exercise: Exercise, request: PlanningRequest) -> bool:
    return exercise.name in request.excluded_exercises


def fits_time(exercise: Exercise, session: SessionPlan, request: PlanningRequest) -> bool:
    return session.total_time + exercise.duration_min <= request.session_time_limit


def fits_fatigue(exercise: Exercise, session: SessionPlan, request: PlanningRequest) -> bool:
    return session.total_fatigue + exercise.fatigue_cost <= request.daily_fatigue_cap


def fits_exercise_count(session: SessionPlan, request: PlanningRequest) -> bool:
    return len(session.exercise_ids) < request.max_exercises_per_session


def has_recovery_conflict(
    exercise: Exercise,
    current_day_index: int,
    last_day_by_category: dict[str, int],
) -> bool:
    if exercise.category not in last_day_by_category:
        return False

    gap = current_day_index - last_day_by_category[exercise.category]
    return gap < exercise.min_recovery_days


def is_feasible(
    exercise: Exercise,
    session: SessionPlan,
    request: PlanningRequest,
    assigned_ids: set[str],
    current_day_index: int,
    last_day_by_category: dict[str, int],
) -> bool:
    if exercise.id in assigned_ids:
        return False
    if is_excluded(exercise, request):
        return False
    if not equipment_is_available(exercise, request):
        return False
    if not fits_time(exercise, session, request):
        return False
    if not fits_fatigue(exercise, session, request):
        return False
    if not fits_exercise_count(session, request):
        return False
    if has_recovery_conflict(exercise, current_day_index, last_day_by_category):
        return False
    return True