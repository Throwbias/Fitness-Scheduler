import os
import copy
import random
import matplotlib.pyplot as plt

# --- Import your actual project modules ---
from src.data_structures.models import PlanningRequest, Individual
from src.ga.operators import GAOperators
from src.ga.evaluator import FitnessEvaluator

# TODO: Import your actual database loader here
# from src.db.connection import get_all_exercises 

def run_experiment(mutation_rate: float, request: PlanningRequest, all_exercises: list, generations: int = 150, pop_size: int = 100):
    """Runs the GA engine and returns a history of the best score per generation."""
    
    print(f"Running simulation with Mutation Rate: {mutation_rate * 100}%...")
    
    # 1. Initialize random Generation 0 population
    population = []
    for _ in range(pop_size):
        ind = Individual()
        for d in request.days_available:
            # Seed with 3 to 6 random exercises per available day
            ind.chromosome[d] = random.choices(all_exercises, k=random.randint(3, 6))
        population.append(ind)

    history = []

    # 2. Evolution Loop
    for gen in range(generations):
        # Evaluate Fitness
        for ind in population:
            ind.score = FitnessEvaluator.evaluate(ind, request)

        # Sort by fitness (descending)
        population.sort(key=lambda x: getattr(x, 'score', 0), reverse=True)
        
        # Record the best score of this generation
        history.append(population[0].score)

        # Build Next Generation
        next_gen = []
        
        # Elitism: Protect the top 5% of the population
        elite_count = int(pop_size * 0.05)
        next_gen.extend(copy.deepcopy(population[:elite_count]))

        # Breed the rest
        while len(next_gen) < pop_size:
            # Tournament Selection (Size 3)
            parent1 = max(random.sample(population, 3), key=lambda x: x.score)
            parent2 = max(random.sample(population, 3), key=lambda x: x.score)

            # Crossover & Mutate using our perfected operators
            child = GAOperators.crossover(parent1, parent2, request)
            
            # This is where we inject the experimental mutation rate!
            GAOperators.mutate(child, request, all_exercises, mutation_rate=mutation_rate)
            
            next_gen.append(child)

        population = next_gen

    return history

if __name__ == "__main__":
    # Ensure the charts directory exists
    os.makedirs('analysis/charts', exist_ok=True)

    # Load your real database
    print("Loading database...")
    # all_exercises = get_all_exercises() # <-- Replace with your actual DB call
    
    # FOR TESTING ONLY: If DB is not hooked up in this script, uncomment below to mock it
    # from src.data_structures.models import Exercise
    # all_exercises = [Exercise(name=f"Ex_{i}", category=random.choice(["Horizontal Push", "Vertical Pull", "Knee Dominant"]), duration_min=10, fatigue_cost=10, priority_score=10) for i in range(70)]

    # The Goldilocks Request
    test_request = PlanningRequest(
        days_available=[0, 2, 4], 
        session_time_limit=60,
        goal="Hypertrophy",
        required_categories=["Horizontal Push", "Vertical Push", "Horizontal Pull", "Vertical Pull", "Hip Dominant", "Knee Dominant", "Elbow Flexion", "Elbow Extension"],
        daily_fatigue_cap=80,
        max_exercises_per_session=6,
        desired_training_days_per_week=3
    )

    # Run the 4 scenarios
    history_0   = run_experiment(0.00, test_request, all_exercises) # Premature Convergence
    history_5   = run_experiment(0.05, test_request, all_exercises) # Sweet Spot A
    history_10  = run_experiment(0.10, test_request, all_exercises) # Sweet Spot B
    history_100 = run_experiment(1.00, test_request, all_exercises) # Pure Chaos

    # Generate the Chart
    print("Generating chart...")
    plt.figure(figsize=(10, 6), dpi=150)

    plt.plot(history_0,   label='0% (Premature Convergence)', color='red', linewidth=2.5, alpha=0.8)
    plt.plot(history_5,   label='5% (Exploitation Heavy)', color='blue', linewidth=2.5, linestyle='--')
    plt.plot(history_10,  label='10% (Optimal Balance)', color='green', linewidth=3.5)
    plt.plot(history_100, label='100% (Pure Chaos)', color='gray', linewidth=1.5, alpha=0.6)

    plt.title('Exploitation vs. Exploration: Empirical Mutation Analysis', fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('Generation', fontsize=12, fontweight='bold')
    plt.ylabel('Best Fitness Score', fontsize=12, fontweight='bold')
    plt.xlim(0, 150)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='lower right', fontsize=11, shadow=True)

    file_path = 'analysis/charts/mutation_rate_empirical.png'
    plt.savefig(file_path, bbox_inches='tight')
    print(f"Chart successfully saved to {file_path}")