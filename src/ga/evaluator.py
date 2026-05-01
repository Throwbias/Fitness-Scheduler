from typing import List
from src.data_structures.models import Individual, PlanningRequest

class GAEvaluator:
    @staticmethod
    def calculate_fitness(individual: Individual, request: PlanningRequest) -> float:
        """
        Judge: Evaluates the quality of a 7-day workout plan.
        Metrics: Priority, Balance, Coverage, and Spacing/Recovery.
        """
        target_day_indices = request.days_available
        if not target_day_indices:
            return 0.01

        # 1. VOLUME-WEIGHTED PRIORITY (Score: 0 - 30)
        # ---------------------------------------------------------
        total_weighted_priority = 0
        for day_idx in target_day_indices:
            for ex in individual.chromosome[day_idx]:
                total_weighted_priority += (ex.priority * ex.duration_min)
        
        max_possible_weighted_priority = len(target_day_indices) * request.session_time_limit * 10
        priority_score = (total_weighted_priority / max_possible_weighted_priority) * 30 if max_possible_weighted_priority > 0 else 0


        # 2. FATIGUE BALANCE / WORKLOAD VARIANCE (Score: 0 - 20)
        # ---------------------------------------------------------
        day_fatigues = [sum(ex.fatigue_cost for ex in individual.chromosome[d]) for d in target_day_indices]
        
        balance_score = 0
        if len(target_day_indices) > 1:
            avg_fatigue = sum(day_fatigues) / len(target_day_indices)
            total_deviation = sum(abs(f - avg_fatigue) for f in day_fatigues)
            avg_deviation = total_deviation / len(target_day_indices)
            balance_score = max(0.0, 20.0 - (avg_deviation * 0.5))
        else:
            balance_score = 20.0


        # 3. CATEGORY COVERAGE (Score: 0 - 50)
        # ---------------------------------------------------------
        category_counts = {}
        for d in target_day_indices:
            for ex in individual.chromosome[d]:
                category_counts[ex.category] = category_counts.get(ex.category, 0) + 1
        
        coverage_points = 0
        req_categories = set(request.required_categories)
        
        for cat in req_categories:
            if category_counts.get(cat, 0) >= 1:
                # 1 point for hitting the required category. No extra credit for spamming it.
                coverage_points += 1.0 

        max_possible_coverage = len(req_categories)
        
        # Calculate the base ratio
        coverage_ratio = (coverage_points / max_possible_coverage) if max_possible_coverage > 0 else 1.0
        final_coverage_pts = coverage_ratio * 50

        # NEW: The "Missing Muscle" Penalty
        missing_categories = max_possible_coverage - coverage_points
        if missing_categories > 0:
            # Deduct 15 points from the TOTAL score for every category it failed to include
            final_coverage_pts -= (missing_categories * 15)

        # 4. SPACING & RECOVERY (Penalty-Based)
        # ---------------------------------------------------------
        spacing_penalty = 0
        # Gather all exercises and their day index for pairwise comparison
        all_scheduled = []
        for d in range(7):
            for ex in individual.chromosome[d]:
                all_scheduled.append({'ex': ex, 'day': d})

        for i, item1 in enumerate(all_scheduled):
            for item2 in all_scheduled[i+1:]:
                ex1, d1 = item1['ex'], item1['day']
                ex2, d2 = item2['ex'], item2['day']

                # Calculate Circular Distance (Sunday to Monday wrap-around)
                raw_dist = abs(d1 - d2)
                dist = min(raw_dist, 7 - raw_dist)

                if dist == 0: continue # Same-day fatigue handles this

                # Check for Muscle Overlap or High-Fatigue (Systemic) Overlap
                is_conflict = (ex1.muscle_group == ex2.muscle_group) or (ex1.priority >= 9 and ex2.priority >= 9)

                if is_conflict:
                    required = max(ex1.min_recovery_days, ex2.min_recovery_days)
                    if dist < required:
                        # Penalty scales: the closer they are, the worse the penalty
                        spacing_penalty += (required - dist) * 10


        # 5. HARD CONSTRAINT VIOLATIONS (The Death Penalty)
        # ---------------------------------------------------------
        violation_penalty = 0
        
        # --- UPDATED: Training Frequency Check (The Breadcrumb Fix) ---
        active_days = individual.get_active_days()
        day_difference = len(active_days) - request.desired_training_days_per_week
        
        if day_difference > 0:
            # SCALING PENALTY: 50 points for EVERY extra day. 
            # 6 extra days = 300 penalty. 1 extra day = 50 penalty.
            violation_penalty += (day_difference * 50) 
            
        elif day_difference < 0:
             # Penalty for scheduling too few days
            violation_penalty += (abs(day_difference) * 50)

        # Existing Time and Fatigue checks below...
        for d in target_day_indices:
            session = individual.chromosome[d]
            day_time = sum(ex.duration_min for ex in session)
            day_fatigue = sum(ex.fatigue_cost for ex in session)
            
            if day_time > request.session_time_limit:
                violation_penalty += 100
            if day_fatigue > request.daily_fatigue_cap:
                violation_penalty += 100

            # Same-Day Duplicate Check (that we added previously)
            seen_exercises = set()
            for ex in session:
                if ex.name in seen_exercises:
                    violation_penalty += 100 
                seen_exercises.add(ex.name)


        # FINAL SCORE SUMMATION
        # ---------------------------------------------------------
        total_fitness = (priority_score + balance_score + final_coverage_pts) - spacing_penalty - violation_penalty
        
        individual.fitness_score = max(0.01, total_fitness)
        return individual.fitness_score