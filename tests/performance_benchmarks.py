import sys
import time
import math
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List

# 1. Define the root path
ROOT_DIR = Path(__file__).resolve().parent.parent

# 2. INJECT it into Python's system path BEFORE importing src!
sys.path.append(str(ROOT_DIR))

# 3. Now Python can safely find your src folder
from src.ga.engine import GeneticSolver
from src.data_structures.models import Exercise, PlanningRequest
from src.db_connector import fetch_all_exercises
from src.utils.loader import load_request

# --- RELIABLE PATH SETUP ---
DATA_DIR = ROOT_DIR / "data"
CHARTS_DIR = ROOT_DIR / "results"

def calculate_stats(data: List[float]):
    """Calculates Mean and Standard Deviation."""
    if not data: return 0, 0
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    return mean, math.sqrt(variance)

def run_benchmarks():
    print("--- Starting Performance Benchmark Suite ---")
    # Ensure the output directory exists
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Exercise Pool
    raw_data = fetch_all_exercises()
    exercise_pool = [
        Exercise(
            id=str(row['ExerciseID']), name=row['Name'], category=row['CategoryName'],
            muscle_group=row['MuscleGroup'], difficulty=row['Difficulty'],
            duration_min=row['EstimatedTimeMins'], fatigue_cost=row['FatigueCost'],
            priority=row['PriorityScore'], min_recovery_days=row['MinRecoveryDays'],
            goal_tags=[]
        ) for row in raw_data
    ]

    # 2. Define Scenarios
    scenarios = {
        "Goldilocks": DATA_DIR / "sample_request.json",
        "Impossible": DATA_DIR / "impossible_request.json"
    }

    all_scenario_scores = {}

    print(f"\n{'Scenario':<15} | {'Avg Time':<10} | {'Avg Score':<12} | {'Stability (SD)':<10}")
    print("-" * 65)

    for name, path in scenarios.items():
        if not path.exists():
            print(f"MISSING FILE: {path}")
            continue

        request = load_request(str(path))
        times, scores = [], []

        # Run 5 iterations for statistical significance
        for i in range(1, 6):
            start = time.perf_counter()
            solver = GeneticSolver(request, exercise_pool, pop_size=100, generations=100)
            best_plan = solver.evolve()
            times.append(time.perf_counter() - start)
            scores.append(best_plan.fitness_score)

        avg_t, _ = calculate_stats(times)
        avg_s, std_s = calculate_stats(scores)
        all_scenario_scores[name] = scores

        print(f"{name:<15} | {avg_t:>8.2f}s | {avg_s:>11.2f} | {std_s:>10.2f}")

    # --- 3. Generate Stability Line Graph ---
    plt.figure(figsize=(10, 6))
    trials = [1, 2, 3, 4, 5]
    
    for name, scores in all_scenario_scores.items():
        plt.plot(trials, scores, marker='o', label=f"{name} (SD: {calculate_stats(scores)[1]:.2f})")

    plt.title('Algorithm Stability: Fitness Scores Over 5 Trials', fontsize=14, fontweight='bold')
    plt.xlabel('Trial Number', fontsize=12)
    plt.ylabel('Fitness Score', fontsize=12)
    plt.xticks(trials)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='best')
    
    # Save to the specific folder
    output_path = CHARTS_DIR / "stability_line.png"
    plt.savefig(output_path)
    plt.close() # Close plot to free up memory
    
    print(f"\n[SUCCESS] Benchmark complete.")
    print(f"[FILE SAVED] {output_path.absolute()}")

if __name__ == "__main__":
    run_benchmarks()