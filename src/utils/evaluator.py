import statistics
from src.data_structures.models import Exercise, PlanningRequest, WeeklyPlan

def compute_coverage_score(plan: WeeklyPlan, request: PlanningRequest) -> float:
    """Calculates the percentage of required movement categories included in the plan."""
    hit_categories = set()
    for session in plan.sessions.values():
        hit_categories.update(session.categories_hit)
    
    required = set(request.required_categories)
    if not required:
        return 1.0
    
    # Calculate ratio of required categories that were actually programmed
    overlap = hit_categories.intersection(required)
    return len(overlap) / len(required)

def compute_priority_score(plan: WeeklyPlan, exercise_lookup: dict[str, Exercise]) -> float:
    """Calculates the mean priority score of all selected exercises."""
    total_priority = 0
    total_exercises = 0
    
    for session in plan.sessions.values():
        for ex_id in session.exercise_ids:
            total_priority += exercise_lookup[ex_id].priority
            total_exercises += 1
            
    if total_exercises == 0:
        return 0.0
    
    # Returns normalized score (assuming max priority is 10)
    return (total_priority / total_exercises) / 10.0

def compute_time_utilization_score(plan: WeeklyPlan, request: PlanningRequest) -> float:
    """Measures how efficiently the programmed sessions use the available time limit."""
    active_sessions = [s for s in plan.sessions.values() if s.exercise_ids]
    if not active_sessions:
        return 0.0
        
    ratios = [s.total_time / request.session_time_limit for s in active_sessions]
    return sum(ratios) / len(active_sessions)

def compute_fatigue_balance_score(plan: WeeklyPlan) -> float:
    """
    Evaluates workload distribution. Returns a higher score for lower variance
    between daily fatigue totals.
    """
    active_fatigue = [s.total_fatigue for s in plan.sessions.values() if s.exercise_ids]
    
    if len(active_fatigue) < 2:
        return 1.0 # Perfectly balanced if only 0 or 1 day is programmed
        
    # Calculate variance; higher variance results in a lower balance score
    var = statistics.pvariance(active_fatigue)
    return max(0.0, 1.0 - (var / 100.0)) # Normalized penalty

def compute_training_frequency_score(plan: WeeklyPlan, request: PlanningRequest) -> float:
    """
    Scores adherence to the user's desired number of training days per week.
    Applies a steep 0.4 penalty for every day of deviation from the target.
    """
    # Count sessions that actually contain exercises
    active_days = sum(1 for s in plan.sessions.values() if s.exercise_ids)
    target = request.desired_training_days_per_week
    
    if target == 0:
        return 1.0
        
    # Calculate absolute difference
    error = abs(active_days - target)
    
    # 0.4 penalty per day off ensures the frequency lever is stronger 
    # than the priority gain from extra exercises.
    # 0 days off = 1.0 | 1 day off = 0.6 | 2 days off = 0.2
    return max(0.0, 1.0 - (error * 0.4))

def count_constraint_violations(
    plan: WeeklyPlan, request: PlanningRequest, exercise_lookup: dict[str, Exercise]
) -> int:
    """Checks for hard constraint violations including recovery windows and fatigue caps."""
    violations = 0
    exercise_last_seen = {} # Tracks chronological placement for recovery checks
    
    # Define standard order for chronological validation
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    sorted_days = sorted(plan.sessions.keys(), key=lambda d: day_order.index(d) if d in day_order else 99)

    for day_idx, day_name in enumerate(sorted_days):
        session = plan.sessions[day_name]
        if not session.exercise_ids:
            continue

        # 1. Hard Constraints
        if session.total_time > request.session_time_limit:
            violations += 1
        if session.total_fatigue > request.daily_fatigue_cap:
            violations += 1
        if len(session.exercise_ids) > request.max_exercises_per_session:
            violations += 1

        # 2. Heavy Lift Limit
        heavy_count = sum(1 for ex_id in session.exercise_ids 
                         if exercise_lookup[ex_id].min_recovery_days >= 2)
        if heavy_count > request.max_heavy_exercises_per_session:
            violations += 1

        # 3. Neurological Recovery Windows
        for ex_id in session.exercise_ids:
            if ex_id in exercise_last_seen:
                days_since = day_idx - exercise_last_seen[ex_id]
                if days_since < exercise_lookup[ex_id].min_recovery_days:
                    violations += 1
            exercise_last_seen[ex_id] = day_idx

    return violations

def evaluate_weekly_plan(
    plan: WeeklyPlan, request: PlanningRequest, exercise_lookup: dict[str, Exercise]
) -> dict:
    """Generates a comprehensive metrics dictionary for the provided plan."""
    
    # Calculate individual metric components
    coverage = compute_coverage_score(plan, request)
    priority = compute_priority_score(plan, exercise_lookup)
    utilization = compute_time_utilization_score(plan, request)
    balance = compute_fatigue_balance_score(plan)
    frequency = compute_training_frequency_score(plan, request)
    violations = count_constraint_violations(plan, request, exercise_lookup)

    # Weighted scoring logic
    total_score = (
        coverage * 25
        + priority * 20
        + utilization * 15
        + balance * 15
        + frequency * 15
        - (violations * 20)
    )

    return {
        "coverage_score": coverage,
        "priority_score": priority,
        "time_utilization_score": utilization,
        "fatigue_balance_score": balance,
        "training_frequency_score": frequency,
        "constraint_violations": violations,
        "total_score": total_score,
    }