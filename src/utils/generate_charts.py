import os
import matplotlib.pyplot as plt
from typing import List

# Core GA Imports
from src.data_structures.models import PlanningRequest, Exercise
from src.db_connector import fetch_all_exercises
from src.ga.engine import GeneticSolver

def get_base_request() -> PlanningRequest:
    """Returns the baseline control request for the experiments."""
    return PlanningRequest(
        days_available=[1, 2, 4, 5],
        session_time_limit=90,
        goal="Hypertrophy",
        required_categories=["Horizontal Push", "Vertical Push", "Horizontal Pull", "Vertical Pull", "Knee Dominant", "Hip Dominant"],
        daily_fatigue_cap=45,
        max_exercises_per_session=8,
        desired_training_days_per_week=4
    )

def experiment_fatigue_cap(exercises: List[Exercise]):
    print("Running Experiment 1: Impact of Daily Fatigue Cap...")
    caps = [15, 25, 35, 45, 55, 65]
    best_scores = []

    for cap in caps:
        req = get_base_request()
        req.daily_fatigue_cap = cap
        # Using fewer generations/pop for faster charting
        solver = GeneticSolver(req, exercises, pop_size=50, generations=80) 
        best_plan = solver.evolve()
        best_scores.append(best_plan.fitness_score)

    plt.figure(figsize=(8, 5))
    plt.plot(caps, best_scores, marker='o', color='crimson', linewidth=2)
    plt.title("Effect of Daily Fatigue Cap on Optimal Fitness Score")
    plt.xlabel("Daily Fatigue Cap (Units)")
    plt.ylabel("Highest Achieved Fitness Score")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig("analysis/charts/exp1_fatigue_cap_impact.png")
    plt.close()

def experiment_time_limit(exercises: List[Exercise]):
    print("Running Experiment 2: Impact of Session Time Limit...")
    times = [30, 45, 60, 90, 120]
    best_scores = []

    for t in times:
        req = get_base_request()
        req.session_time_limit = t
        solver = GeneticSolver(req, exercises, pop_size=50, generations=80)
        best_plan = solver.evolve()
        best_scores.append(best_plan.fitness_score)

    plt.figure(figsize=(8, 5))
    plt.plot(times, best_scores, marker='s', color='teal', linewidth=2)
    plt.title("Effect of Session Time Limit on Optimal Fitness Score")
    plt.xlabel("Session Time Limit (Minutes)")
    plt.ylabel("Highest Achieved Fitness Score")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig("analysis/charts/exp2_time_limit_impact.png")
    plt.close()

def experiment_population_size(exercises: List[Exercise]):
    print("Running Experiment 3: Population Size vs. Convergence Speed...")
    sizes = [10, 50, 150]
    histories = {}

    req = get_base_request()
    for size in sizes:
        solver = GeneticSolver(req, exercises, pop_size=size, generations=100)
        solver.evolve()
        histories[size] = solver.history

    plt.figure(figsize=(10, 6))
    colors = ['gray', 'blue', 'purple']
    for (size, history), color in zip(histories.items(), colors):
        plt.plot(history, label=f'Pop Size: {size}', color=color, linewidth=2)
    
    plt.title("Convergence Speed by Population Size")
    plt.xlabel("Generation")
    plt.ylabel("Best Fitness Score")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig("analysis/charts/exp3_population_convergence.png")
    plt.close()

def main():
    # Ensure the directory exists
    os.makedirs("analysis/charts", exist_ok=True)

    print("Fetching exercises from database...")
    raw = fetch_all_exercises()
    exercises = [
        Exercise(
            str(e['ExerciseID']), e['Name'], e['CategoryName'], e['MuscleGroup'], 
            e['Difficulty'], e['EstimatedTimeMins'], e['FatigueCost'], 
            e['PriorityScore'], e['MinRecoveryDays'], []
        ) for e in raw
    ]

    if not exercises:
        print("Error: Could not load exercises. Check database connection.")
        return

    experiment_fatigue_cap(exercises)
    experiment_time_limit(exercises)
    experiment_population_size(exercises)

    print("\nAll experiments complete! Check the 'analysis/charts' folder for your new graphs.")

if __name__ == "__main__":
    main()