from copy import deepcopy

from src.utils.evaluator import evaluate_weekly_plan
from src.utils.filters import is_feasible
from src.utils.scoring import candidate_score


def recompute_session(session, lookup):
    session.total_time = sum(
        lookup[ex_id].duration_min for ex_id in session.exercise_ids
    )
    session.total_fatigue = sum(
        lookup[ex_id].fatigue_cost for ex_id in session.exercise_ids
    )
    session.categories_hit = []
    for ex_id in session.exercise_ids:
        cat = lookup[ex_id].category
        if cat not in session.categories_hit:
            session.categories_hit.append(cat)


def reset_session(session):
    session.exercise_ids = []
    session.total_time = 0
    session.total_fatigue = 0
    session.categories_hit = []


def session_is_meaningful(session, request):
    return (
        len(session.exercise_ids) >= request.min_exercises_per_session
        and session.total_time >= request.min_session_time_for_training_day
    )


def build_weekly_state(plan, request, exercise_lookup):
    assigned_ids = set()
    category_counts_this_week = {}
    last_day_by_category = {}

    day_to_index = {day: idx for idx, day in enumerate(request.days_available)}

    for day in request.days_available:
        session = plan.sessions[day]
        for ex_id in session.exercise_ids:
            ex = exercise_lookup[ex_id]
            assigned_ids.add(ex_id)
            category_counts_this_week[ex.category] = (
                category_counts_this_week.get(ex.category, 0) + 1
            )
            last_day_by_category[ex.category] = day_to_index[day]

    return assigned_ids, category_counts_this_week, last_day_by_category, day_to_index


def count_heavy_exercises(session, exercise_lookup):
    return sum(
        1 for ex_id in session.exercise_ids if exercise_lookup[ex_id].fatigue_cost >= 6
    )


def try_build_session_on_empty_day(
    trial_plan,
    day,
    exercises,
    request,
    exercise_lookup,
):
    """
    Attempt to build a meaningful session on an empty day using currently unused exercises.
    Returns (success: bool, updated_plan)
    """
    assigned_ids, category_counts_this_week, last_day_by_category, day_to_index = (
        build_weekly_state(trial_plan, request, exercise_lookup)
    )

    active_days = sum(
        1 for s in trial_plan.sessions.values() if len(s.exercise_ids) > 0
    )

    session = trial_plan.sessions[day]
    day_index = day_to_index[day]

    while True:
        feasible = [
            ex
            for ex in exercises
            if ex.id not in assigned_ids
            and is_feasible(
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

        current_heavy = count_heavy_exercises(session, exercise_lookup)
        feasible = [
            ex
            for ex in feasible
            if not (
                ex.fatigue_cost >= 6
                and current_heavy >= request.max_heavy_exercises_per_session
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
        category_counts_this_week[best.category] = (
            category_counts_this_week.get(best.category, 0) + 1
        )
        last_day_by_category[best.category] = day_index

    if session_is_meaningful(session, request):
        return True, trial_plan

    reset_session(session)
    return False, trial_plan


def refine_plan_with_replacements(
    plan, exercises, request, exercise_lookup, max_iterations=100
):
    """
    Optimizes an existing weekly workout plan using a local search algorithm.

    This algorithm iteratively explores a neighborhood of adjacent schedules to find
    a global optimum. It attempts four types of mutations per iteration:
        1. Replacement: Swapping an assigned exercise with an unused one.
        2. Insertion: Building a new valid session on a previously empty day.
        3. Relocation: Moving an exercise to an empty day and building a new session around it.
        4. Swapping: Trading exercises between two already active days to balance fatigue.

    Any mutation that improves the overall `total_score` while strictly adhering
    to all hard constraints (time limits, fatigue caps, recovery) is kept.
    The search terminates when an iteration completes with no improvements found,
    or when max_iterations is reached.

    Time Complexity:
        Approximately O(I * D^2 * K^2 * N) in the worst case, where I is the number
        of iterations, D is active days, K is exercises per session, and N is the
        number of available unused exercises.

    Args:
        plan (WeeklyPlan): The initial feasible plan (usually generated via a greedy heuristic).
        exercises (list[Exercise]): The complete list of available Exercise objects.
        request (PlanningRequest): The user's configuration and hard constraints.
        exercise_lookup (dict[str, Exercise]): O(1) lookup dictionary mapping exercise IDs to objects.
        max_iterations (int, optional): The maximum number of improvement loops to execute. Defaults to 100.

    Returns:
        tuple[WeeklyPlan, dict]: A tuple containing the fully optimized WeeklyPlan
        and a dictionary of its final evaluated metrics.
    """
    best_plan = deepcopy(plan)
    best_metrics = evaluate_weekly_plan(best_plan, request, exercise_lookup)

    for _ in range(max_iterations):
        improved = False

        # --------------------------------------------------
        # MOVE TYPE 1: replacement inside existing sessions
        # --------------------------------------------------
        assigned_ids, _, _, _ = build_weekly_state(best_plan, request, exercise_lookup)
        unused_exercises = [ex for ex in exercises if ex.id not in assigned_ids]

        for day in request.days_available:
            session = best_plan.sessions[day]

            if len(session.exercise_ids) == 0:
                continue

            for i, current_ex_id in enumerate(session.exercise_ids):
                for candidate in unused_exercises:
                    trial_plan = deepcopy(best_plan)
                    trial_lookup = dict(exercise_lookup)
                    trial_lookup[candidate.id] = candidate

                    trial_session = trial_plan.sessions[day]
                    trial_session.exercise_ids[i] = candidate.id
                    recompute_session(trial_session, trial_lookup)

                    if trial_session.total_time > request.session_time_limit:
                        continue
                    if trial_session.total_fatigue > request.daily_fatigue_cap:
                        continue
                    if (
                        count_heavy_exercises(trial_session, trial_lookup)
                        > request.max_heavy_exercises_per_session
                    ):
                        continue
                    if not session_is_meaningful(trial_session, request):
                        continue

                    trial_metrics = evaluate_weekly_plan(
                        trial_plan, request, trial_lookup
                    )

                    if trial_metrics["total_score"] > best_metrics["total_score"]:
                        best_plan = trial_plan
                        best_metrics = trial_metrics
                        exercise_lookup = trial_lookup
                        improved = True
                        break

                if improved:
                    break
            if improved:
                break

        if improved:
            continue

        # --------------------------------------------------
        # MOVE TYPE 2: insert a new session on an empty day
        # --------------------------------------------------
        active_days = sum(
            1 for s in best_plan.sessions.values() if len(s.exercise_ids) > 0
        )

        if active_days < request.max_training_days_per_week:
            for day in request.days_available:
                session = best_plan.sessions[day]

                if len(session.exercise_ids) > 0:
                    continue

                candidate_plan = deepcopy(best_plan)
                success, candidate_plan = try_build_session_on_empty_day(
                    candidate_plan,
                    day,
                    exercises,
                    request,
                    exercise_lookup,
                )

                if not success:
                    continue

                candidate_metrics = evaluate_weekly_plan(
                    candidate_plan, request, exercise_lookup
                )

                if candidate_metrics["total_score"] > best_metrics["total_score"]:
                    best_plan = candidate_plan
                    best_metrics = candidate_metrics
                    improved = True
                    break

        if improved:
            continue

        # --------------------------------------------------
        # MOVE TYPE 3: relocate one exercise from active day
        #               to an empty day, then try to build it up
        # --------------------------------------------------
        active_days = sum(
            1 for s in best_plan.sessions.values() if len(s.exercise_ids) > 0
        )

        if active_days < request.max_training_days_per_week:
            empty_days = [
                day
                for day in request.days_available
                if len(best_plan.sessions[day].exercise_ids) == 0
            ]

            source_days = [
                day
                for day in request.days_available
                if len(best_plan.sessions[day].exercise_ids) >= 3
            ]

            for source_day in source_days:
                for target_day in empty_days:
                    source_session = best_plan.sessions[source_day]

                    for idx, ex_id_to_move in enumerate(source_session.exercise_ids):
                        trial_plan = deepcopy(best_plan)
                        trial_lookup = dict(exercise_lookup)

                        trial_source = trial_plan.sessions[source_day]
                        trial_target = trial_plan.sessions[target_day]

                        # Move one exercise from source to empty target
                        moved_ex_id = trial_source.exercise_ids.pop(idx)
                        trial_target.exercise_ids.append(moved_ex_id)

                        recompute_session(trial_source, trial_lookup)
                        recompute_session(trial_target, trial_lookup)

                        # Source must still remain meaningful
                        if len(
                            trial_source.exercise_ids
                        ) > 0 and not session_is_meaningful(trial_source, request):
                            continue

                        # Initial target day may be too small; try to build it up
                        success, trial_plan = try_build_session_on_empty_day(
                            trial_plan,
                            target_day,
                            exercises,
                            request,
                            trial_lookup,
                        )

                        if not success:
                            continue

                        # Final legality checks
                        valid = True
                        for sess in trial_plan.sessions.values():
                            if sess.total_time > request.session_time_limit:
                                valid = False
                                break
                            if sess.total_fatigue > request.daily_fatigue_cap:
                                valid = False
                                break
                            if (
                                count_heavy_exercises(sess, trial_lookup)
                                > request.max_heavy_exercises_per_session
                            ):
                                valid = False
                                break

                        if not valid:
                            continue

                        candidate_metrics = evaluate_weekly_plan(
                            trial_plan, request, trial_lookup
                        )

                        if (
                            candidate_metrics["total_score"]
                            > best_metrics["total_score"]
                        ):
                            best_plan = trial_plan
                            best_metrics = candidate_metrics
                            exercise_lookup = trial_lookup
                            improved = True
                            break

                    if improved:
                        break
                if improved:
                    break

        if improved:
            continue

        # --------------------------------------------------
        # MOVE TYPE 4: Swap exercises between two active days
        # --------------------------------------------------
        active_days_list = [
            day
            for day in request.days_available
            if len(best_plan.sessions[day].exercise_ids) > 0
        ]

        for i in range(len(active_days_list)):
            for j in range(i + 1, len(active_days_list)):
                day1 = active_days_list[i]
                day2 = active_days_list[j]

                session1 = best_plan.sessions[day1]
                session2 = best_plan.sessions[day2]

                for idx1, ex_id_1 in enumerate(session1.exercise_ids):
                    for idx2, ex_id_2 in enumerate(session2.exercise_ids):

                        trial_plan = deepcopy(best_plan)
                        trial_lookup = dict(exercise_lookup)

                        trial_session1 = trial_plan.sessions[day1]
                        trial_session2 = trial_plan.sessions[day2]

                        # Perform the swap
                        trial_session1.exercise_ids[idx1] = ex_id_2
                        trial_session2.exercise_ids[idx2] = ex_id_1

                        recompute_session(trial_session1, trial_lookup)
                        recompute_session(trial_session2, trial_lookup)

                        # Validity checks for both sessions
                        valid = True
                        for sess in (trial_session1, trial_session2):
                            if sess.total_time > request.session_time_limit:
                                valid = False
                                break
                            if sess.total_fatigue > request.daily_fatigue_cap:
                                valid = False
                                break
                            if (
                                count_heavy_exercises(sess, trial_lookup)
                                > request.max_heavy_exercises_per_session
                            ):
                                valid = False
                                break

                        if not valid:
                            continue

                        # Ensure both sessions are still meaningful after the swap
                        if not session_is_meaningful(
                            trial_session1, request
                        ) or not session_is_meaningful(trial_session2, request):
                            continue

                        trial_metrics = evaluate_weekly_plan(
                            trial_plan, request, trial_lookup
                        )

                        if trial_metrics["total_score"] > best_metrics["total_score"]:
                            best_plan = trial_plan
                            best_metrics = trial_metrics
                            improved = True
                            break

                    if improved:
                        break
                if improved:
                    break

        if not improved:
            break

    return best_plan, best_metrics
