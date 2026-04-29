from copy import deepcopy
from src.utils.evaluator import evaluate_weekly_plan
from src.utils.filters import is_feasible
from src.utils.scoring import candidate_score

def recompute_session(session, lookup):
    """Updates session totals and categories after a mutation."""
    session.total_time = sum(lookup[ex_id].duration_min for ex_id in session.exercise_ids)
    session.total_fatigue = sum(lookup[ex_id].fatigue_cost for ex_id in session.exercise_ids)
    session.categories_hit = list(set(lookup[ex_id].category for ex_id in session.exercise_ids))

def reset_session(session):
    """Clears a session completely."""
    session.exercise_ids = []
    session.total_time = 0
    session.total_fatigue = 0
    session.categories_hit = []

def session_is_meaningful(session, request):
    """Ensures a session meets the minimum volume and duration requirements."""
    return (len(session.exercise_ids) >= request.min_exercises_per_session and 
            session.total_time >= request.min_session_time_for_training_day)

def build_weekly_state(plan, request, exercise_lookup):
    """Aggregates global plan state for feasibility checks."""
    assigned_ids = set()
    category_counts = {}
    last_day_by_cat = {}
    day_to_idx = {day: idx for idx, day in enumerate(request.days_available)}

    for day in request.days_available:
        for ex_id in plan.sessions[day].exercise_ids:
            ex = exercise_lookup[ex_id]
            assigned_ids.add(ex_id)
            category_counts[ex.category] = category_counts.get(ex.category, 0) + 1
            last_day_by_cat[ex.category] = day_to_idx[day]
            
    return assigned_ids, category_counts, last_day_by_cat, day_to_idx

def count_heavy_exercises(session, exercise_lookup):
    """Helper to count high-fatigue movements (>= 6) in a session."""
    return sum(1 for ex_id in session.exercise_ids if exercise_lookup[ex_id].fatigue_cost >= 6)

def try_build_session_on_empty_day(trial_plan, day, exercises, request, exercise_lookup):
    """Attempt to populate an empty day using a greedy heuristic."""
    assigned_ids, category_counts, last_day_by_cat, day_to_idx = build_weekly_state(trial_plan, request, exercise_lookup)
    active_days = sum(1 for s in trial_plan.sessions.values() if s.exercise_ids)
    session = trial_plan.sessions[day]
    day_index = day_to_idx[day]

    while True:
        feasible = [ex for ex in exercises if ex.id not in assigned_ids and 
                    is_feasible(ex, session, request, assigned_ids, day_index, last_day_by_cat)]
        
        # Respect heavy lift limits
        current_heavy = count_heavy_exercises(session, exercise_lookup)
        feasible = [ex for ex in feasible if not (ex.fatigue_cost >= 6 and current_heavy >= request.max_heavy_exercises_per_session)]

        if not feasible: break

        ranked = sorted(feasible, key=lambda ex: candidate_score(ex, session, request, category_counts, active_days), reverse=True)
        best = ranked[0]
        
        # Stop if no remaining exercises provide enough value
        score = candidate_score(best, session, request, category_counts, active_days)
        if (not session.exercise_ids and score < request.min_start_score) or (session.exercise_ids and score < request.min_continue_score):
            break

        session.exercise_ids.append(best.id)
        recompute_session(session, exercise_lookup)
        assigned_ids.add(best.id)
        category_counts[best.category] = category_counts.get(best.category, 0) + 1
        last_day_by_cat[best.category] = day_index

    if session_is_meaningful(session, request):
        return True, trial_plan
    reset_session(session)
    return False, trial_plan

def refine_plan_with_replacements(plan, exercises, request, exercise_lookup, max_iterations=1000):
    """
    Optimizes a weekly plan using Hill Climbing across four mutation types.
    """
    print(f"\n[DEBUG] Starting Local Search (Limit: {max_iterations} iterations)")
    
    best_plan = deepcopy(plan)
    best_metrics = evaluate_weekly_plan(best_plan, request, exercise_lookup)

    for iteration in range(1, max_iterations + 1):
        improved = False

        # --- MOVE TYPE 1: Replacement (Intra-session swap) ---
        assigned_ids, _, _, _ = build_weekly_state(best_plan, request, exercise_lookup)
        unused_exercises = [ex for ex in exercises if ex.id not in assigned_ids]

        for day in request.days_available:
            session = best_plan.sessions[day]
            if not session.exercise_ids: continue

            for i, current_ex_id in enumerate(session.exercise_ids):
                for candidate in unused_exercises:
                    trial_plan = deepcopy(best_plan)
                    trial_session = trial_plan.sessions[day]
                    trial_session.exercise_ids[i] = candidate.id
                    recompute_session(trial_session, exercise_lookup)

                    # Validation
                    if (trial_session.total_time <= request.session_time_limit and 
                        trial_session.total_fatigue <= request.daily_fatigue_cap and 
                        count_heavy_exercises(trial_session, exercise_lookup) <= request.max_heavy_exercises_per_session and
                        session_is_meaningful(trial_session, request)):
                        
                        trial_metrics = evaluate_weekly_plan(trial_plan, request, exercise_lookup)
                        if trial_metrics["total_score"] > best_metrics["total_score"]:
                            best_plan, best_metrics, improved = trial_plan, trial_metrics, True
                            break
                if improved: break
            if improved: break
        if improved: continue

        # --- MOVE TYPE 2: Insertion (New session on empty day) ---
        active_days = sum(1 for s in best_plan.sessions.values() if s.exercise_ids)
        if active_days < request.max_training_days_per_week:
            for day in request.days_available:
                if best_plan.sessions[day].exercise_ids: continue
                
                success, trial_plan = try_build_session_on_empty_day(deepcopy(best_plan), day, exercises, request, exercise_lookup)
                if success:
                    trial_metrics = evaluate_weekly_plan(trial_plan, request, exercise_lookup)
                    if trial_metrics["total_score"] > best_metrics["total_score"]:
                        best_plan, best_metrics, improved = trial_plan, trial_metrics, True
                        break
        if improved: continue

        # --- MOVE TYPE 3: Relocation (Move 1 exercise, then build around it) ---
        empty_days = [d for d in request.days_available if not best_plan.sessions[d].exercise_ids]
        source_days = [d for d in request.days_available if len(best_plan.sessions[d].exercise_ids) >= 3]

        if empty_days and active_days < request.max_training_days_per_week:
            for target_day in empty_days:
                for source_day in source_days:
                    source_session = best_plan.sessions[source_day]
                    for idx, ex_id in enumerate(source_session.exercise_ids):
                        trial_plan = deepcopy(best_plan)
                        trial_source = trial_plan.sessions[source_day]
                        trial_target = trial_plan.sessions[target_day]

                        # Relocate
                        moved_id = trial_source.exercise_ids.pop(idx)
                        trial_target.exercise_ids.append(moved_id)
                        
                        recompute_session(trial_source, exercise_lookup)
                        recompute_session(trial_target, exercise_lookup)

                        # Try building the target day further
                        success, trial_plan = try_build_session_on_empty_day(trial_plan, target_day, exercises, request, exercise_lookup)
                        if success:
                            # Final validation of both affected sessions
                            if session_is_meaningful(trial_plan.sessions[source_day], request):
                                trial_metrics = evaluate_weekly_plan(trial_plan, request, exercise_lookup)
                                if trial_metrics["total_score"] > best_metrics["total_score"]:
                                    best_plan, best_metrics, improved = trial_plan, trial_metrics, True
                                    break
                    if improved: break
                if improved: break
        if improved: continue

        # --- MOVE TYPE 4: Swapping (Inter-session swap) ---
        active_days_list = [d for d in request.days_available if best_plan.sessions[d].exercise_ids]
        for i, d1 in enumerate(active_days_list):
            for d2 in active_days_list[i+1:]:
                for idx1, id1 in enumerate(best_plan.sessions[d1].exercise_ids):
                    for idx2, id2 in enumerate(best_plan.sessions[d2].exercise_ids):
                        trial_plan = deepcopy(best_plan)
                        trial_plan.sessions[d1].exercise_ids[idx1] = id2
                        trial_plan.sessions[d2].exercise_ids[idx2] = id1

                        recompute_session(trial_plan.sessions[d1], exercise_lookup)
                        recompute_session(trial_plan.sessions[d2], exercise_lookup)

                        # Validate both sessions for time, fatigue, and volume
                        valid = True
                        for d in [d1, d2]:
                            s = trial_plan.sessions[d]
                            if (s.total_time > request.session_time_limit or 
                                s.total_fatigue > request.daily_fatigue_cap or 
                                not session_is_meaningful(s, request)):
                                valid = False; break
                        
                        if valid:
                            trial_metrics = evaluate_weekly_plan(trial_plan, request, exercise_lookup)
                            if trial_metrics["total_score"] > best_metrics["total_score"]:
                                best_plan, best_metrics, improved = trial_plan, trial_metrics, True
                                break
                    if improved: break
                if improved: break
        if improved: continue

        if not improved:
            print(f"[INFO] Local Optimum reached at iteration {iteration}.")
            break

    return best_plan, best_metrics