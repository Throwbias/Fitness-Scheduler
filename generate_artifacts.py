import sys
import time
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

# --- GUARANTEED PATH SETUP ---
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

try:
    from src.ga.engine import GeneticSolver
    from src.db_connector import fetch_all_exercises
    from src.utils.loader import load_request
    from src.data_structures.models import Exercise
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

# --- RESULTS DIRECTORY ---
RESULTS_DIR = ROOT_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("🚀 Starting Experimental Artifact Generation...")
    
    # 1. Load Data
    raw_data = fetch_all_exercises()
    pool = [Exercise(
        id=str(r['ExerciseID']), name=r['Name'], category=r['CategoryName'],
        muscle_group=r['MuscleGroup'], difficulty=r['Difficulty'],
        duration_min=r['EstimatedTimeMins'], fatigue_cost=r['FatigueCost'],
        priority=r['PriorityScore'], min_recovery_days=r['MinRecoveryDays'], goal_tags=[]
    ) for r in raw_data]
    
    request = load_request(str(ROOT_DIR / "data" / "sample_request.json"))
    print(f"✅ Data loaded: {len(pool)} exercises found.")

    # --- ARTIFACT 1: Scaling Benchmarks ---
    print("\n📊 Generating Scaling Benchmarks...")
    pop_sizes = [20, 50, 100, 150]
    times = []
    for p in pop_sizes:
        start = time.perf_counter()
        GeneticSolver(request, pool, pop_size=p, generations=25).evolve()
        times.append(time.perf_counter() - start)

    plt.figure(figsize=(8, 5))
    plt.bar([str(p) for p in pop_sizes], times, color='teal', edgecolor='black')
    plt.title("Computational Scaling: Execution Time vs Population Size", fontweight='bold')
    plt.xlabel("Population Size")
    plt.ylabel("Execution Time (Seconds)")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(RESULTS_DIR / "01_scaling_performance.png")
    plt.close()

    # --- ARTIFACT 2: Final Plan Analysis ---
    print("\n🧬 Running High-Gen Evolution for Plan Analysis...")
    best_solver = GeneticSolver(request, pool, pop_size=100, generations=100)
    
    result = best_solver.evolve()
    best_individual = result[0] if isinstance(result, list) else result
    
    # --- NEW: FORMAT-AGNOSTIC DATA EXTRACTION ---
    # We check if the chromosome is a dict or a list to avoid AttributeErrors
    chrom = best_individual.chromosome
    
    if isinstance(chrom, dict):
        days_labels = [f"Day {d}" for d in chrom.keys()]
        sessions = list(chrom.values())
    else:  # It's a list (as per your AttributeError)
        days_labels = [f"Day {i+1}" for i in range(len(chrom))]
        sessions = chrom

    # Extract metrics for plotting
    fatigue = [sum(ex.fatigue_cost for ex in session) for session in sessions]
    time_spent = [sum(ex.duration_min for ex in session) for session in sessions]
    all_exercises = [ex for session in sessions for ex in session]
    categories = [ex.category for ex in all_exercises]
    cat_counts = Counter(categories)

    # Plot: Fatigue Distribution
    print("📈 Plotting Fatigue and Time Utilization...")
    plt.figure(figsize=(8, 5))
    plt.bar(days_labels, fatigue, color='coral', edgecolor='black')
    plt.axhline(request.daily_fatigue_cap, color='red', linestyle='--', label='Fatigue Cap')
    plt.title("Workload Distribution (Fatigue Management)", fontweight='bold')
    plt.ylabel("Cumulative Fatigue")
    plt.legend()
    plt.savefig(RESULTS_DIR / "02_fatigue_distribution.png")
    plt.close()

    # Plot: Time Utilization
    plt.figure(figsize=(8, 5))
    plt.bar(days_labels, time_spent, color='skyblue', edgecolor='black')
    plt.axhline(request.session_time_limit, color='darkred', linestyle='--', label='Time Limit')
    plt.title("Session Time Utilization", fontweight='bold')
    plt.ylabel("Minutes")
    plt.legend()
    plt.savefig(RESULTS_DIR / "03_time_utilization.png")
    plt.close()

    # Plot: Exercise Category Mix
    print("🍕 Plotting Category Distribution...")
    plt.figure(figsize=(7, 7))
    plt.pie(cat_counts.values(), labels=cat_counts.keys(), autopct='%1.1f%%', colors=plt.cm.Paired.colors)
    plt.title("Exercise Volume by Biomechanical Category", fontweight='bold')
    plt.savefig(RESULTS_DIR / "04_category_mix.png")
    plt.close()

    print(f"\n✨ SUCCESS! 4 new artifacts added to: {RESULTS_DIR}")

if __name__ == "__main__":
    main()