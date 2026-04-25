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
    """
    Constructs a feasible weekly workout plan using a greedy heuristic.

    This algorithm iterates through available training days iteratively, 
    evaluating and assigning the highest-scoring valid exercise based on 
    the candidate_score heuristic. It natively respects hard constraints 
    including daily fatigue caps, session time limits, and recovery windows.

    Time Complexity:
        O(D * N * K) where D is the number of available days, N is the 
        number of exercises, and K is the maximum exercises per session.

    Args:
        exercises (list[Exercise]): A list of all available Exercise objects.
        request (PlanningRequest): The user's configuration and constraint parameters.

    Returns:
        WeeklyPlan: A populated weekly schedule that satisfies all hard constraints.
    """
    sessions = {
        day: SessionPlan(day=day)
        for day in request.days_available
    }

    plan = WeeklyPlan(sessions=sessions)

    assigned_ids = set()
    category_counts_this_week = {}
    last_day_by_category = {}
    exercise_lookup = {ex.id: ex for ex in exercises}

    days = spread_days(request.days_available)

    # Use a flag to keep the loop running as long as we are finding valid placements
    making_progress = True 
    
    while making_progress:
        making_progress = False # Reset at the start of each week cycle
        
        # Iterate through the days, adding exactly ONE exercise per day
        for day_index, day in enumerate(days):
            
            # Check training day limit dynamically based on populated sessions
            active_days = sum(1 for s in plan.sessions.values() if len(s.exercise_ids) > 0)
            
            session = plan.sessions[day]
            
            # If the session is empty and we've hit our day limit, skip it
            if len(session.exercise_ids) == 0 and active_days >= request.max_training_days_per_week:
                continue

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
                continue

            ranked = sorted(
                feasible,
                key=lambda ex: candidate_score(
                    ex,
                    session,
                    request,
                    category_counts_this_week,
                    training_days_used=active_days,
                ),
                reverse=True,
            )

            best = ranked[0]
            best_score = candidate_score(
                best,
                session,
                request,
                category_counts_this_week,
                training_days_used=active_days,
            )

            current_heavy = sum(
                1 for ex_id in session.exercise_ids
                if exercise_lookup[ex_id].fatigue_cost >= 6
            )
            
            if best.fatigue_cost >= 6 and current_heavy >= request.max_heavy_exercises_per_session:
                continue

            if len(session.exercise_ids) == 0:
                if best_score < request.min_start_score:
                    continue
            else:
                if best_score < request.min_continue_score:
                    continue

            # Add the best exercise to this day
            session.exercise_ids.append(best.id)
            session.total_time += best.duration_min
            session.total_fatigue += best.fatigue_cost

            if best.category not in session.categories_hit:
                session.categories_hit.append(best.category)

            assigned_ids.add(best.id)
            category_counts_this_week[best.category] = category_counts_this_week.get(best.category, 0) + 1
            last_day_by_category[best.category] = day_index
            
            # Since we successfully added an exercise, we know we made progress
            making_progress = True

    # Cleanup phase: remove any sessions that don't meet the meaningful threshold
    # This must happen at the end because a session might need multiple passes to become meaningful
    for day in days:
        session = plan.sessions[day]
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

    return plan