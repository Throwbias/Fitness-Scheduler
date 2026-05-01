from src.data_structures.models import SessionPlan, WeeklyPlan
from src.utils.filters import is_feasible
from src.utils.scoring import candidate_score

DAY_MAP = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}

def reset_session(session: SessionPlan):
    session.exercise_ids, session.total_time, session.total_fatigue, session.categories_hit = [], 0, 0, []

def session_is_meaningful(session: SessionPlan, request) -> bool:
    return len(session.exercise_ids) >= request.min_exercises_per_session and session.total_time >= request.min_session_time_for_training_day

def build_greedy_plan(exercises, request):
    sessions = {day: SessionPlan(day=day) for day in request.days_available}
    plan = WeeklyPlan(sessions=sessions)
    assigned_ids, category_counts, last_day_by_cat = set(), {}, {}
    exercise_lookup = {ex.id: ex for ex in exercises}

    making_progress = True
    while making_progress:
        making_progress = False
        for day in request.days_available:
            session = plan.sessions[day]
            day_idx = DAY_MAP[day]
            
            feasible = [ex for ex in exercises if is_feasible(ex, session, request, assigned_ids, day_idx, last_day_by_cat)]
            
            current_heavy = sum(1 for eid in session.exercise_ids if exercise_lookup[eid].min_recovery_days >= 2)
            feasible = [ex for ex in feasible if not (ex.min_recovery_days >= 2 and current_heavy >= request.max_heavy_exercises_per_session)]

            if not feasible: continue

            best = sorted(feasible, key=lambda x: candidate_score(x, session, request, category_counts), reverse=True)[0]
            
            session.exercise_ids.append(best.id)
            session.total_time += best.duration_min
            session.total_fatigue += best.fatigue_cost
            if best.category not in session.categories_hit: session.categories_hit.append(best.category)

            assigned_ids.add(best.id)
            category_counts[best.category] = category_counts.get(best.category, 0) + 1
            last_day_by_cat[best.category] = day_idx
            making_progress = True

    for day, session in plan.sessions.items():
        if len(session.exercise_ids) > 0 and not session_is_meaningful(session, request):
            for eid in session.exercise_ids: assigned_ids.discard(eid)
            reset_session(session)
    return plan