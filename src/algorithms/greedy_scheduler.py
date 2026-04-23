from src.data_structures.models import SessionPlan, WeeklyPlan
from src.utils.filters import is_feasible
from src.utils.scoring import candidate_score


def spread_days(days_available):
    days = list(days_available)
    order = []
    left = 0
    right = len(days) - 1

    while left <= right:
        order.append(days[left])
        left += 1
        if left <= right:
            order.append(days[right])
            right -= 1

    return order


def reset_session(session: SessionPlan):
    session.exercise_ids = []
    session.total_time = 0
    session.total_fatigue = 0
    session.categories_hit = []


def session_is_meaningful(session: SessionPlan, request) -> bool:
    return (
        len(session.exercise_ids) >= request.min_exercises_per_session
        and session.total_time >= request.min_session_time_for_training_day
    )


def build_greedy_plan(exercises, request):
    sessions = {
        day: SessionPlan(day=day)
        for day in request.days_available
    }

    plan = WeeklyPlan(sessions=sessions)

    assigned_ids = set()
    category_counts_this_week = {}
    last_day_by_category = {}
    training_days_used = 0
    exercise_lookup = {ex.id: ex for ex in exercises}

    days = spread_days(request.days_available)

    for day_index, day in enumerate(days):
        if training_days_used >= request.max_training_days_per_week:
            break

        session = plan.sessions[day]

        while True:
            feasible = [
                ex for ex in exercises
                if is_feasible(
                    exercise=ex,
                    session=session,
                    request=request,
                    assigned_ids=assigned_ids,
                    current_day_index=day_index,
                    last_day_by_category=last_day_by_category,
                )
            ]

            if not feasible:
                break

            ranked = sorted(
                feasible,
                key=lambda ex: candidate_score(
                    ex,
                    session,
                    request,
                    category_counts_this_week,
                    training_days_used=training_days_used,
                ),
                reverse=True,
            )

            best = ranked[0]
            best_score = candidate_score(
                best,
                session,
                request,
                category_counts_this_week,
                training_days_used=training_days_used,
            )

            current_heavy = sum(
                1 for ex_id in session.exercise_ids
                if exercise_lookup[ex_id].fatigue_cost >= 6
            )
            if best.fatigue_cost >= 6 and current_heavy >= request.max_heavy_exercises_per_session:
                break

            if len(session.exercise_ids) == 0:
                if best_score < request.min_start_score:
                    break
            else:
                if best_score < request.min_continue_score:
                    break

            session.exercise_ids.append(best.id)
            session.total_time += best.duration_min
            session.total_fatigue += best.fatigue_cost

            if best.category not in session.categories_hit:
                session.categories_hit.append(best.category)

            assigned_ids.add(best.id)
            category_counts_this_week[best.category] = category_counts_this_week.get(best.category, 0) + 1
            last_day_by_category[best.category] = day_index

        if len(session.exercise_ids) > 0 and not session_is_meaningful(session, request):
            for ex_id in session.exercise_ids:
                assigned_ids.discard(ex_id)
                ex = exercise_lookup[ex_id]
                category_counts_this_week[ex.category] = max(
                    0, category_counts_this_week.get(ex.category, 1) - 1
                )
                if category_counts_this_week[ex.category] == 0:
                    del category_counts_this_week[ex.category]
            reset_session(session)

        if len(session.exercise_ids) > 0:
            training_days_used += 1

    return plan