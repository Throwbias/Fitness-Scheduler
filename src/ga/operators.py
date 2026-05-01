import random
import copy
from typing import List
from src.data_structures.models import Individual, PlanningRequest, Exercise

class GAOperators:
    """
    The Genetic Engine. 
    This handles 'mating' (combining two good plans) and 'mutation' (randomly 
    tweaking a plan) to keep the AI discovering better workouts instead of 
    getting stuck in a rut.
    """

    @staticmethod
    def crossover(parent1: Individual, parent2: Individual, request: PlanningRequest) -> Individual:
        """
        Day-Level Mating. 
        We treat each full day of exercises as a solid block. The 'child' plan 
        flips a coin for every available day: heads it inherits Parent A's routine, 
        tails it inherits Parent B's.
        """
        child = Individual()
        
        for d in range(7):
            if d in request.days_available:
                source_parent = parent1 if random.random() < 0.5 else parent2
                
                # We use deepcopy here! If we just link the lists, any future mutations
                # to the child would accidentally overwrite the parent's memory too.
                child.chromosome[d] = copy.deepcopy(source_parent.chromosome[d])
            else:
                # Force rest days to stay completely empty
                child.chromosome[d] = []
                
        return child

    @staticmethod
    def mutate(individual: Individual, request: PlanningRequest, all_exercises: List[Exercise], mutation_rate: float = 0.1):
        """
        The Mutation Engine. 
        Randomly alters the workout plan. This prevents the AI from getting stuck 
        doing the exact same "okay" workout forever by forcing it to try new things.
        """
        active_days = individual.get_active_days()
        
        # --- THE SUPER-NUKE (Fixing the Frequency Trap) ---
        # If the AI scheduled workouts on 6 days, but the user only wanted 3, it's trapped.
        # Deleting exercises one-by-one is too slow, and the AI will die from penalties.
        # This gives it a 5% chance to instantly delete all the extra days at once.
        if len(active_days) > request.desired_training_days_per_week:
            if random.random() < 0.05:
                # Pick the exact number of days the user actually wanted to keep
                days_to_keep = random.sample(active_days, request.desired_training_days_per_week)
                
                # Instantly wipe out everything else
                for day in active_days:
                    if day not in days_to_keep:
                        individual.chromosome[day] = []
                        
                # This is a massive change, so we return early and skip standard mutations.
                return 

        # --- STANDARD MUTATIONS ---
        # 10% chance to run a normal mutation
        if random.random() > mutation_rate:
            return

        # Pick a random way to mess with the schedule
        mutation_type = random.choice(["point", "relocation", "swap"])

        if mutation_type == "point":
            GAOperators._apply_point_mutation(individual, request, all_exercises)
        elif mutation_type == "relocation":
            GAOperators._apply_relocation_mutation(individual, request)
        elif mutation_type == "swap":
            GAOperators._apply_swap_mutation(individual, request)

    @staticmethod
    def _apply_point_mutation(individual: Individual, request: PlanningRequest, all_exercises: List[Exercise]):
        """
        Point Mutation (Discovering new things). 
        Grabs a random exercise currently in the plan and replaces it with a 
        completely new one from the database.
        """
        active_days = individual.get_active_days()
        if not active_days: return

        day_idx = random.choice(active_days)
        if not individual.chromosome[day_idx]: return

        ex_idx = random.randrange(len(individual.chromosome[day_idx]))
        individual.chromosome[day_idx][ex_idx] = random.choice(all_exercises)

    @staticmethod
    def _apply_relocation_mutation(individual: Individual, request: PlanningRequest):
        """
        Relocation (Balancing the workload). 
        Moves an exercise from one day to another. If Monday is hitting the fatigue 
        limit, this might randomly bump Monday's Deadlifts over to Wednesday.
        """
        active_days = individual.get_active_days()
        allowed_days = request.days_available
        if not active_days or len(allowed_days) < 2: return

        source_day = random.choice(active_days)
        if not individual.chromosome[source_day]: return
        
        # Pull the exercise out of its current day
        ex = individual.chromosome[source_day].pop(random.randrange(len(individual.chromosome[source_day])))

        # Drop it into a new, valid day
        dest_day = random.choice([d for d in allowed_days if d != source_day])
        individual.chromosome[dest_day].append(ex)

    @staticmethod
    def _apply_swap_mutation(individual: Individual, request: PlanningRequest):
        """
        Swap (Fixing recovery time). 
        Takes two exercises on different days and swaps them. This helps the AI 
        figure out that heavy squats and deadlifts shouldn't happen two days in a row.
        """
        allowed_days = request.days_available
        if len(allowed_days) < 2: return

        day_a, day_b = random.sample(allowed_days, 2)
        
        if not individual.chromosome[day_a] or not individual.chromosome[day_b]:
            return

        idx_a = random.randrange(len(individual.chromosome[day_a]))
        idx_b = random.randrange(len(individual.chromosome[day_b]))

        # Swap the exercises in memory
        individual.chromosome[day_a][idx_a], individual.chromosome[day_b][idx_b] = \
            individual.chromosome[day_b][idx_b], individual.chromosome[day_a][idx_a]