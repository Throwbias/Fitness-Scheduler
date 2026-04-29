import random
from src.filters import is_feasible
from src.models import SessionPlan, WeeklyPlan
from src.scoring import candidate_score

# 1. Map days to actual calendar indices to fix recovery math
DAY_MAP = {
    "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
    "Friday": 4, "Saturday": 5, "Sunday": 6
}

def session_is_meaningful(session: SessionPlan, request) -> bool:
    """Ensures a session provides sufficient training stimulus."""
    return (
        len(session.exercise_ids) >= request.min_exercises_per_session
        and session.total_time >= request.min_session_time_for_training_day
    )

def reset_session(session: SessionPlan):
    """Wipes a session if it doesn't meet meaningful thresholds."""
    session.exercise_ids = []
    session.total_time = 0
    session.total_fatigue = 0
    session.categories_hit = []

def build_greedy_plan(exercises, request):
    sessions = {day: SessionPlan(day=day) for day in request.days_available}
    plan = WeeklyPlan(sessions=sessions)

    assigned_ids = set()
    categories_hit_this_week = set()
    last_day_by_category = {}
    exercise_lookup = {ex.id: ex for ex in exercises}

    for day in request.days_available:
        session = plan.sessions[day]
        # Use actual calendar index for recovery math
        current_calendar_idx = DAY_MAP.get(day, 0)

        while True:
            # 2. Filter for feasibility
            feasible = [
                ex for ex in exercises
                if is_feasible(ex, session, request, assigned_ids, current_calendar_idx, last_day_by_category)
            ]

            if not feasible:
                break

            # 3. Apply the "Heavy" lift limit (Min Recovery >= 2 days)
            current_heavy_count = sum(
                1 for eid in session.exercise_ids 
                if exercise_lookup[eid].min_recovery_days >= 2
            )
            
            feasible = [
                ex for ex in feasible
                if not (ex.min_recovery_days >= 2 and current_heavy_count >= request.max_heavy_exercises_per_session)
            ]

            if not feasible:
                break

            # 4. Score and select the best move
            ranked = sorted(
                feasible,
                key=lambda ex: candidate_score(ex, session, request, categories_hit_this_week),
                reverse=True
            )

            best = ranked[0]

            # Add to session
            session.exercise_ids.append(best.id)
            session.total_time += best.duration_min
            session.total_fatigue += best.fatigue_cost
            if best.category not in session.categories_hit:
                session.categories_hit.append(best.category)

            # Update tracking
            assigned_ids.add(best.id)
            categories_hit_this_week.add(best.category)
            last_day_by_category[best.category] = current_calendar_idx

    # 5. Cleanup Phase: Ensure all sessions are meaningful
    for day, session in plan.sessions.items():
        if len(session.exercise_ids) > 0 and not session_is_meaningful(session, request):
            # If a day isn't meaningful, release the exercises and wipe it
            for eid in session.exercise_ids:
                assigned_ids.discard(eid)
            reset_session(session)

    return plan

def build_random_plan(exercises, request, seed=None):
    rng = random.Random(seed)
    sessions = {day: SessionPlan(day=day) for day in request.days_available}
    plan = WeeklyPlan(sessions=sessions)

    assigned_ids = set()
    categories_hit_this_week = set()
    last_day_by_category = {}
    exercise_lookup = {ex.id: ex for ex in exercises}

    for day in request.days_available:
        session = plan.sessions[day]
        current_calendar_idx = DAY_MAP.get(day, 0)

        while True:
            feasible = [
                ex for ex in exercises
                if is_feasible(ex, session, request, assigned_ids, current_calendar_idx, last_day_by_category)
            ]

            if not feasible:
                break

            # Random also respects the heavy lift limit
            current_heavy_count = sum(
                1 for eid in session.exercise_ids 
                if exercise_lookup[eid].min_recovery_days >= 2
            )
            feasible = [
                ex for ex in feasible
                if not (ex.min_recovery_days >= 2 and current_heavy_count >= request.max_heavy_exercises_per_session)
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
            last_day_by_category[chosen.category] = current_calendar_idx

        if len(session.exercise_ids) > 0 and not session_is_meaningful(session, request):
            for eid in session.exercise_ids:
                assigned_ids.discard(eid)
            reset_session(session)

    return plan