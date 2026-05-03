from typing import List
from src.data_structures.models import Individual, PlanningRequest

class GAEvaluator:
    """
    The 'Judge' of the system. This class implements the objective function 
    that converts a workout plan (chromosome) into a single fitness score.
    
    It balances four primary goals:
    1. Maximizing exercise priority
    2. Minimizing workload variance (Balance)
    3. Ensuring complete muscle group coverage
    4. Enforcing biological recovery windows
    """

    @staticmethod
    def calculate_fitness(individual: Individual, request: PlanningRequest) -> float:
        """
        Calculates the cumulative fitness score for a 7-day schedule.
        """
        target_day_indices = request.days_available
        if not target_day_indices:
            return 0.01

        # --- 1. VOLUME-WEIGHTED PRIORITY ---
        # Rewards the selection of high-value exercises (Compound lifts) 
        # while accounting for their time commitment.
        total_weighted_priority = 0
        for day_idx in target_day_indices:
            for ex in individual.chromosome[day_idx]:
                total_weighted_priority += (ex.priority * ex.duration_min)
        
        max_possible = len(target_day_indices) * request.session_time_limit * 10
        priority_score = (total_weighted_priority / max_possible) * 30 if max_possible > 0 else 0

        # --- 2. FATIGUE BALANCE (VARIANCE MINIMIZATION) ---
        # Rewards schedules where every training day has a similar workload.
        day_fatigues = [sum(ex.fatigue_cost for ex in individual.chromosome[d]) for d in target_day_indices]
        
        if len(target_day_indices) > 1:
            avg_fatigue = sum(day_fatigues) / len(target_day_indices)
            avg_deviation = sum(abs(f - avg_fatigue) for f in day_fatigues) / len(target_day_indices)
            balance_score = max(0.0, 20.0 - (avg_deviation * 0.5))
        else:
            balance_score = 20.0

        # --- 3. CATEGORY COVERAGE ---
        # Ensures all requested movement patterns (Squat, Hinge, Push, etc.) are present.
        coverage_points = 0
        req_categories = set(request.required_categories)
        hit_counts = {}

        for d in target_day_indices:
            for ex in individual.chromosome[d]:
                hit_counts[ex.category] = hit_counts.get(ex.category, 0) + 1
        
        for cat in req_categories:
            if hit_counts.get(cat, 0) >= 1:
                coverage_points += 1.0

        max_cov = len(req_categories)
        coverage_ratio = (coverage_points / max_cov) if max_cov > 0 else 1.0
        final_coverage_pts = coverage_ratio * 50

        # Missing Muscle Penalty: Severe deduction for incomplete programs.
        missing = max_cov - coverage_points
        if missing > 0:
            final_coverage_pts -= (missing * 30.0) 

        # --- 4. SPACING & RECOVERY (CIRCULAR DISTANCE MATH) ---
        # Punishes back-to-back heavy lifting or muscle group overlap.
        spacing_penalty = 0
        all_scheduled = []
        for d in range(7):
            for ex in individual.chromosome[d]:
                all_scheduled.append({'ex': ex, 'day': d})

        for i, item1 in enumerate(all_scheduled):
            for item2 in all_scheduled[i+1:]:
                ex1, d1 = item1['ex'], item1['day']
                ex2, d2 = item2['ex'], item2['day']

                # Account for Sunday-to-Monday wrap-around
                raw_dist = abs(d1 - d2)
                dist = min(raw_dist, 7 - raw_dist)
                if dist == 0: continue

                is_conflict = (ex1.muscle_group == ex2.muscle_group) or (ex1.priority >= 9 and ex2.priority >= 9)
                if is_conflict:
                    required = max(ex1.min_recovery_days, ex2.min_recovery_days)
                    if dist < required:
                        spacing_penalty += (required - dist) * 10

        # --- 5. CONSTRAINT VIOLATIONS (THE DEATH PENALTY) ---
        # Hard limits on time, fatigue, frequency, and repetition.
        violation_penalty = 0
        
        # Frequency Check
        active_days = individual.get_active_days()
        day_diff = abs(len(active_days) - request.desired_training_days_per_week)
        violation_penalty += (day_diff * 50)

        weekly_exercise_counts = {} 
        
        # Added: Density Bonus tracking
        density_bonus = 0

        for d in target_day_indices:
            session = individual.chromosome[d]
            s_time = sum(ex.duration_min for ex in session)
            s_fatigue = sum(ex.fatigue_cost for ex in session)

            # Density Reward Logic: Fight the "Lazy GA" syndrome
            if s_time > 0:
                utilization = s_time / request.session_time_limit
                if utilization >= 0.8:
                    density_bonus += 15.0  # Reward for full sessions
                elif utilization < 0.4:
                    density_bonus -= 10.0  # Penalty for slacker sessions

            if s_time > request.session_time_limit:
                violation_penalty += 100
            if s_fatigue > request.daily_fatigue_cap:
                violation_penalty += 100

            seen_today = set()
            for ex in session:
                if ex.name in seen_today: violation_penalty += 100
                seen_today.add(ex.name)
                weekly_exercise_counts[ex.name] = weekly_exercise_counts.get(ex.name, 0) + 1

        # Anti-Spam Penalty: High cost for repeating the same lift across multiple days.
        for count in weekly_exercise_counts.values():
            if count > 1:
                violation_penalty += ((count - 1) * 40.0)

        # Final Calculation including the new density_bonus
        total_fitness = (priority_score + balance_score + final_coverage_pts + density_bonus) - spacing_penalty - violation_penalty
        individual.fitness_score = max(0.01, total_fitness)
        return individual.fitness_score