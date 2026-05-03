import random
from typing import List
from src.data_structures.models import Individual, Exercise, PlanningRequest
from src.ga.evaluator import GAEvaluator
from src.ga.operators import GAOperators

class GeneticSolver:
    def __init__(
        self, 
        request: PlanningRequest, 
        exercise_pool: List[Exercise], 
        pop_size: int = 250,
        generations: int = 200
    ):
        self.request = request
        self.exercise_pool = exercise_pool
        self.pop_size = pop_size
        self.generations = generations
        self.population: List[Individual] = []
        self.history: List[float] = [] 

    def _selection(self, tournament_size: int = 3) -> Individual:
        tournament = random.sample(self.population, k=tournament_size)
        return max(tournament, key=lambda ind: ind.fitness_score)

    def evolve(self) -> Individual:
        self._initialize_population()
        
        for gen in range(self.generations):
            for ind in self.population:
                GAEvaluator.calculate_fitness(ind, self.request)
            
            self.population.sort(key=lambda x: x.fitness_score, reverse=True)
            self.history.append(self.population[0].fitness_score)

            # --- REIMPLEMENTED: Generation Progress Printing ---
            if gen % 10 == 0:
                print(f"Gen {gen:3} | Best Score: {self.population[0].fitness_score:.2f}")

            new_population: List[Individual] = []
            elite_count = max(1, int(self.pop_size * 0.05))
            new_population.extend(self.population[:elite_count])

            while len(new_population) < self.pop_size:
                p1 = self._selection()
                p2 = self._selection()
                child = GAOperators.crossover(p1, p2, self.request)
                GAOperators.mutate(child, self.request, self.exercise_pool)
                new_population.append(child)

            self.population = new_population

        # Final score update before returning
        for ind in self.population:
            GAEvaluator.calculate_fitness(ind, self.request)
        self.population.sort(key=lambda x: x.fitness_score, reverse=True)

        # Print the final completion message
        print(f"Gen {self.generations} | Final Best Score: {self.population[0].fitness_score:.2f}")
        
        return self.population[0]

    def _initialize_population(self) -> None:
        self.population = []
        for _ in range(self.pop_size):
            ind = Individual()
            for d_idx in self.request.days_available:
                count = random.randint(1, self.request.max_exercises_per_session)
                ind.chromosome[d_idx] = random.sample(self.exercise_pool, k=count)
            self.population.append(ind)