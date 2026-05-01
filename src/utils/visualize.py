import matplotlib.pyplot as plt
from src.data_structures.models import PlanningRequest
from src.ga.engine import GeneticSolver
from src.db_connector import fetch_all_exercises
from src.data_structures.models import Exercise

def plot_evolution():
    # 1. Fetch data
    raw_exercises = fetch_all_exercises()
    exercises = [Exercise(str(e['ExerciseID']), e['Name'], e['CategoryName'], e['MuscleGroup'], 
                 e['Difficulty'], e['EstimatedTimeMins'], e['FatigueCost'], e['PriorityScore'], 
                 e['MinRecoveryDays'], []) for e in raw_exercises]

    # 2. Set your parameters
    request = PlanningRequest(
        days_available=[1, 2, 4, 5],
        session_time_limit=90,
        goal="Hypertrophy",
        required_categories=["Horizontal Push", "Vertical Push", "Horizontal Pull", "Vertical Pull", "Knee Dominant", "Hip Dominant"],
        daily_fatigue_cap=45,
        max_exercises_per_session=10,
        desired_training_days_per_week=4
    )

    # 3. Run the GA
    solver = GeneticSolver(request, exercises, pop_size=100, generations=150)
    best_plan = solver.evolve()

    # 4. Plot the results
    plt.figure(figsize=(10, 6))
    plt.plot(solver.history, color='b', linewidth=2)
    plt.title("Genetic Algorithm Evolution: Fitness Score over 150 Generations", fontsize=14)
    plt.xlabel("Generation", fontsize=12)
    plt.ylabel("Best Fitness Score", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Save the chart to your analysis folder
    plt.savefig("analysis/charts/evolution_curve.png")
    print("\nSaved evolution chart to analysis/charts/evolution_curve.png")

if __name__ == "__main__":
    plot_evolution()