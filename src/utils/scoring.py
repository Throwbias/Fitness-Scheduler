from src.data_structures.models import Exercise, PlanningRequest, SessionPlan


LOWER_CATEGORIES = {"squat", "hinge"}
UPPER_CATEGORIES = {"push", "pull"}
SUPPORT_CATEGORIES = {"core"}
PRIMARY_CATEGORIES = {"squat", "hinge"}


def same_focus(first_category: str, new_category: str) -> bool:
    if first_category in LOWER_CATEGORIES and new_category in LOWER_CATEGORIES:
        return True
    if first_category in UPPER_CATEGORIES and new_category in UPPER_CATEGORIES:
        return True
    if new_category in SUPPORT_CATEGORIES:
        return True
    return False


def target_session_time(request: PlanningRequest) -> float:
    preference_map = {
        "light": 0.50,
        "moderate": 0.65,
        "substantial": 0.80,
    }
    fraction = preference_map.get(request.session_fullness_preference, 0.65)
    return request.session_time_limit * fraction


def candidate_score(
    exercise: Exercise,
    session: SessionPlan,
    request: PlanningRequest,
    category_counts_this_week,
    training_days_used: int = 0,
) -> float:
    if isinstance(category_counts_this_week, dict):
        weekly_count = category_counts_this_week.get(exercise.category, 0)
    else:
        weekly_count = 1 if exercise.category in category_counts_this_week else 0

    priority_term = exercise.priority
    category_need = 8 if weekly_count == 0 else max(0, 3 - weekly_count)

    remaining_time = request.session_time_limit - session.total_time
    time_fit = max(0, 4 - abs(remaining_time - exercise.duration_min) / 8)

    goal_alignment = 5 if request.goal in exercise.goal_tags else 0
    preferred_bonus = 3 if exercise.name in request.preferred_exercises else 0

    projected_fatigue = session.total_fatigue + exercise.fatigue_cost
    fatigue_penalty = 4.5 * (projected_fatigue / request.daily_fatigue_cap)

    if len(session.exercise_ids) == 0:
        session_saturation_penalty = 0
    elif len(session.exercise_ids) == 1:
        session_saturation_penalty = 1.5
    elif len(session.exercise_ids) == 2:
        session_saturation_penalty = 3.5
    else:
        session_saturation_penalty = 6

    repeated_category_penalty = 2 if exercise.category in session.categories_hit else 0

    # Opening a new day is good, especially if we are below desired weekly frequency
    if len(session.exercise_ids) == 0:
        new_day_bonus = 6

        if training_days_used < request.desired_training_days_per_week:
            frequency_bonus = 2 + (request.desired_training_days_per_week - training_days_used)
        else:
            frequency_bonus = 0
    else:
        new_day_bonus = 0
        frequency_bonus = 0

    unique_categories = len(set(session.categories_hit + [exercise.category]))
    coherence_penalty = max(0, unique_categories - 3) * 2

    if len(session.categories_hit) == 0:
        focus_bonus = 0
        primary_bonus = 2 if exercise.category in PRIMARY_CATEGORIES else 0
    else:
        first_category = session.categories_hit[0]
        focus_bonus = 3 if same_focus(first_category, exercise.category) else 0

        if first_category in PRIMARY_CATEGORIES and same_focus(first_category, exercise.category):
            primary_bonus = 2
        else:
            primary_bonus = 0

    target_time = target_session_time(request)
    projected_time = session.total_time + exercise.duration_min

    if projected_time <= target_time:
        fill_bonus = 10 * (projected_time / target_time)
    else:
        fill_bonus = max(
            0,
            10 - ((projected_time - target_time) / 8)
        )

    return (
        priority_term
        + category_need
        + time_fit
        + goal_alignment
        + preferred_bonus
        + new_day_bonus
        + frequency_bonus
        + focus_bonus
        + primary_bonus
        + fill_bonus
        - fatigue_penalty
        - session_saturation_penalty
        - repeated_category_penalty
        - coherence_penalty
    )