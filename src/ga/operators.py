import random
import copy
from typing import List
from src.data_structures.models import Individual, PlanningRequest, Exercise

class GAOperators:
    """
    The Genetic Lab: Responsible for the mechanical manipulation of 
    workout plan DNA through Crossover and Mutation.
    """

    @staticmethod
    def crossover(parent1: Individual, parent2: Individual, request: PlanningRequest) -> Individual:
        """
        Performs Uniform Crossover at the Day-level.
        Inherits entire workout sessions from parents to preserve session logic.
        """
        child = Individual()
        
        for d in range(7):
            if d in request.days_available:
                # 50/50 chance to inherit the day's routine from either parent
                source_parent = parent1 if random.random() < 0.5 else parent2
                # CRITICAL: Deepcopy prevents the child from modifying the parent's data
                child.chromosome[d] = copy.deepcopy(source_parent.chromosome[d])
            else:
                # Strictly enforce rest days
                child.chromosome[d] = []
                
        return child

    @staticmethod
    def mutate(individual: Individual, request: PlanningRequest, all_exercises: List[Exercise], mutation_rate: float = 0.1):
        """
        Decides if a mutation occurs and which type of structural change to apply.
        """
        if random.random() > mutation_rate:
            return

        # We use three types of mutation to ensure the AI explores the full solution space
        mutation_type = random.choice(["point", "relocation", "swap"])

        if mutation_type == "point":
            GAOperators._apply_point_mutation(individual, request, all_exercises)
        elif mutation_type == "relocation":
            GAOperators._apply_relocation_mutation(individual, request)
        elif mutation_type == "swap":
            GAOperators._apply_swap_mutation(individual, request)

    @staticmethod
    def _apply_point_mutation(individual: Individual, request: PlanningRequest, all_exercises: List[Exercise]):
        """Replaces a random exercise with a new one from the database (Discovery)."""
        active_days = individual.get_active_days()
        if not active_days: return

        day_idx = random.choice(active_days)
        if not individual.chromosome[day_idx]: return

        ex_idx = random.randrange(len(individual.chromosome[day_idx]))
        # Swap out the existing gene for a fresh one from the pool
        individual.chromosome[day_idx][ex_idx] = random.choice(all_exercises)

    @staticmethod
    def _apply_relocation_mutation(individual: Individual, request: PlanningRequest):
        """Moves an exercise to a different allowed training day (Workload Balancing)."""
        active_days = individual.get_active_days()
        allowed_days = request.days_available
        if not active_days or len(allowed_days) < 2: return

        source_day = random.choice(active_days)
        if not individual.chromosome[source_day]: return
        
        # Pull the exercise out of its current day
        ex = individual.chromosome[source_day].pop(random.randrange(len(individual.chromosome[source_day])))

        # Find a different allowed day to move it to
        dest_day = random.choice([d for d in allowed_days if d != source_day])
        individual.chromosome[dest_day].append(ex)

    @staticmethod
    def _apply_swap_mutation(individual: Individual, request: PlanningRequest):
        """Swaps two exercises between different allowed days (Spacing Optimization)."""
        allowed_days = request.days_available
        if len(allowed_days) < 2: return

        # Pick two different days
        day_a, day_b = random.sample(allowed_days, 2)
        
        # Ensure both days have at least one exercise to swap
        if not individual.chromosome[day_a] or not individual.chromosome[day_b]:
            return

        idx_a = random.randrange(len(individual.chromosome[day_a]))
        idx_b = random.randrange(len(individual.chromosome[day_b]))

        # The actual swap
        individual.chromosome[day_a][idx_a], individual.chromosome[day_b][idx_b] = \
            individual.chromosome[day_b][idx_b], individual.chromosome[day_a][idx_a]