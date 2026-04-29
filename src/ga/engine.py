import random
from typing import List, Tuple
from src.data_structures.models import Individual, Exercise, PlanningRequest
from src.ga.evaluator import GAEvaluator
from src.ga.operators import GAOperators

class GeneticSolver:
    def __init__(
        self, 
        request: PlanningRequest, 
        exercise_pool: List[Exercise], 
        pop_size: int = 100,
        generations: int = 100,
        elitism_count: int = 2
    ):
        self.request = request
        self.exercise_pool = exercise_pool
        self.pop_size = pop_size
        self.generations = generations
        self.elitism_count = elitism_count
        self.population: List[Individual] = []

    def _selection(self, tournament_size: int = 3) -> Individual:
        """
        Tournament Selection: Picks the best of a random subset.
        """
        # Pick 'k' random candidates from the population
        tournament = random.sample(self.population, k=tournament_size)
        
        # The one with the highest fitness score wins
        return max(tournament, key=lambda ind: ind.fitness_score)

    def evolve(self) -> Individual:
        """
        The main evolutionary loop.
        """
        # 1. Initialization (We wrote the logic for this earlier)
        self._initialize_population()
        
        for gen in range(self.generations):
            # 2. Evaluation: Score every member of the current population
            for individual in self.population:
                GAEvaluator.calculate_fitness(individual, self.request)
            
            # Sort population by fitness (Best first)
            self.population.sort(key=lambda x: x.fitness_score, reverse=True)
            
            # Print Progress (Optional)
            if gen % 10 == 0:
                print(f"Gen {gen} | Best Score: {self.population[0].fitness_score:.2f}")

            new_population = []

            # 3. Elitism: Keep the absolute best plans from the previous generation
            new_population.extend(self.population[:self.elitism_count])

            # 4. Fill the rest of the new population
            while len(new_population) < self.pop_size:
                # Selection
                parent1 = self._selection()
                parent2 = self._selection()
                
                # Crossover (Mating)
                child = GAOperators.crossover(parent1, parent2, self.request)
                
                # Mutation (Variation)
                GAOperators.mutate(child, self.request, self.exercise_pool)
                
                new_population.append(child)

            self.population = new_population

        # Final Evaluation of the last generation
        for individual in self.population:
            GAEvaluator.calculate_fitness(individual, self.request)
        self.population.sort(key=lambda x: x.fitness_score, reverse=True)
        
        return self.population[0] # Return the GOAT (Greatest of All Time)

    def _initialize_population(self):
        """Builds Gen 0: Random plans assigned to allowed days."""
        self.population = []
        for _ in range(self.pop_size):
            ind = Individual()
            for d_idx in self.request.days_available:
                # Start with a random number of exercises per allowed day
                count = random.randint(1, self.request.max_exercises_per_session)
                ind.chromosome[d_idx] = random.sample(self.exercise_pool, k=count)
            self.population.append(ind)