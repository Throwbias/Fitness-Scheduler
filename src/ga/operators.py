import random
import copy
from typing import List
from src.data_structures.models import Individual, PlanningRequest, Exercise

class GAOperators:
    """
    Biological Logic Layer: Handles the creation of new genetic material 
    via Crossover (mating) and random variation (Mutation).
    """

    @staticmethod
    def crossover(parent1: Individual, parent2: Individual, request: PlanningRequest) -> Individual:
        """
        Uniform Day-Level Crossover.
        Each day in the child's schedule is inherited as a complete block from 
        either Parent A or Parent B, preserving the internal session structure.
        """
        child = Individual()
        for d in range(7):
            if d in request.days_available:
                source = parent1 if random.random() < 0.5 else parent2
                # Use deepcopy to ensure child mutations don't affect parents in memory
                child.chromosome[d] = copy.deepcopy(source.chromosome[d])
            else:
                child.chromosome[d] = []
        return child

    @staticmethod
    def mutate(individual: Individual, request: PlanningRequest, all_exercises: List[Exercise], mutation_rate: float = 0.1) -> None:
        """
        The Mutation Engine: Randomly alters the individual to prevent 
        local minimum stagnation and maintain genetic diversity.
        """
        active_days = individual.get_active_days()
        
        # --- THE SUPER-NUKE (Targeted Frequency Correction) ---
        if len(active_days) > request.desired_training_days_per_week:
            if random.random() < 0.05:
                to_keep = random.sample(active_days, request.desired_training_days_per_week)
                for d in active_days:
                    if d not in to_keep:
                        individual.chromosome[d] = []
                return 

        # Standard Mutation Logic
        if random.random() > mutation_rate:
            return

        # Choose a mutation strategy based on the specific scheduling need
        m_type = random.choice(["point", "relocation", "swap"])

        if m_type == "point":
            GAOperators._apply_point_mutation(individual, all_exercises)
        elif m_type == "relocation":
            GAOperators._apply_relocation_mutation(individual, request)
        elif m_type == "swap":
            GAOperators._apply_swap_mutation(individual, request)

    @staticmethod
    def _apply_point_mutation(individual: Individual, all_exercises: List[Exercise]) -> None:
        """Randomly replaces one exercise in the plan with a new one from the database."""
        active_days = individual.get_active_days()
        if not active_days: return
        day_idx = random.choice(active_days)
        if not individual.chromosome[day_idx]: return
        ex_idx = random.randrange(len(individual.chromosome[day_idx]))
        individual.chromosome[day_idx][ex_idx] = random.choice(all_exercises)

    @staticmethod
    def _apply_relocation_mutation(individual: Individual, request: PlanningRequest) -> None:
        """Moves an exercise from one training day to another available day."""
        active_days = individual.get_active_days()
        if not active_days or len(request.days_available) < 2: return
        source_day = random.choice(active_days)
        if not individual.chromosome[source_day]: return
        ex = individual.chromosome[source_day].pop(random.randrange(len(individual.chromosome[source_day])))
        dest_day = random.choice([d for d in request.days_available if d != source_day])
        individual.chromosome[dest_day].append(ex)

    @staticmethod
    def _apply_swap_mutation(individual: Individual, request: PlanningRequest) -> None:
        """Swaps two exercises between different days to optimize spacing/recovery."""
        allowed = request.days_available
        if len(allowed) < 2: return
        day_a, day_b = random.sample(allowed, 2)
        if not individual.chromosome[day_a] or not individual.chromosome[day_b]: return
        idx_a = random.randrange(len(individual.chromosome[day_a]))
        idx_b = random.randrange(len(individual.chromosome[day_b]))
        individual.chromosome[day_a][idx_a], individual.chromosome[day_b][idx_b] = \
            individual.chromosome[day_b][idx_b], individual.chromosome[day_a][idx_a]