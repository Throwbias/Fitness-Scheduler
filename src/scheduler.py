import random

from src.filters import is_feasible
from src.models import SessionPlan, WeeklyPlan
from src.scoring import candidate_score


def build_greedy_plan(exercises, request):
    sessions = {day: SessionPlan(day=day) for day in request.days_available}

    plan = WeeklyPlan(sessions=sessions)

    assigned_ids = set()
    categories_hit_this_week = set()
    last_day_by_category = {}

    for day_index, day in enumerate(request.days_available):
        session = plan.sessions[day]

        while True:
            feasible = [
                ex
                for ex in exercises
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
                    ex, session, request, categories_hit_this_week
                ),
                reverse=True,
            )

            best = ranked[0]

            session.exercise_ids.append(best.id)
            session.total_time += best.duration_min
            session.total_fatigue += best.fatigue_cost

            if best.category not in session.categories_hit:
                session.categories_hit.append(best.category)

            assigned_ids.add(best.id)
            categories_hit_this_week.add(best.category)
            last_day_by_category[best.category] = day_index

    return plan


def build_random_plan(exercises, request, seed=None):
    rng = random.Random(seed)

    sessions = {day: SessionPlan(day=day) for day in request.days_available}

    plan = WeeklyPlan(sessions=sessions)

    assigned_ids = set()
    categories_hit_this_week = set()
    last_day_by_category = {}

    for day_index, day in enumerate(request.days_available):
        session = plan.sessions[day]

        while True:
            feasible = [
                ex
                for ex in exercises
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

            chosen = rng.choice(feasible)

            session.exercise_ids.append(chosen.id)
            session.total_time += chosen.duration_min
            session.total_fatigue += chosen.fatigue_cost

            if chosen.category not in session.categories_hit:
                session.categories_hit.append(chosen.category)

            assigned_ids.add(chosen.id)
            categories_hit_this_week.add(chosen.category)
            last_day_by_category[chosen.category] = day_index

    return plan
