import argparse
import logging
import time

# Core Algorithms
from src.algorithms.greedy_scheduler import build_greedy_plan
from src.algorithms.local_search import refine_plan_with_replacements
from src.algorithms.random_scheduler import build_random_plan

# Utilities and Data Structures
from src.data_structures.models import Exercise
from src.db_connector import fetch_all_exercises
from src.utils.evaluator import evaluate_weekly_plan
from src.utils.experiment_runner import save_results
from src.utils.loader import load_request
from src.utils.printer import print_schedule, print_metrics_comparison

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    parser = argparse.ArgumentParser(description="Constraint-Based Fitness Scheduler")
    parser.add_argument("--request", type=str, default="data/sample_request.json")
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()

    logging.info("Initializing Constraint-Based Fitness Scheduler...")

    # --- 1. DATA LOADING PHASE ---
    logging.info("Connecting to SQL Server to fetch exercise library...")
    raw_exercises = fetch_all_exercises()
    
    if not raw_exercises:
        logging.error("No exercises found! Please check your database connection.")
        return
        
    exercises = []
    for ex_data in raw_exercises:
        raw_tags = ex_data.get('GoalTags', "")
        tags_list = [tag.strip() for tag in raw_tags.split(',')] if raw_tags else []
        exercises.append(
            Exercise(
                id=ex_data['ExerciseID'],
                name=ex_data['Name'],
                category=ex_data['CategoryName'],
                muscle_group=ex_data['MuscleGroup'],
                difficulty=ex_data['Difficulty'],
                duration_min=ex_data['EstimatedTimeMins'],
                fatigue_cost=ex_data['FatigueCost'],
                priority=ex_data['PriorityScore'],
                min_recovery_days=ex_data['MinRecoveryDays'],
                goal_tags=tags_list
            )
        )
    
    logging.info(f"Successfully loaded {len(exercises)} exercises.")
    exercise_lookup = {ex.id: ex for ex in exercises}
    request = load_request(args.request)

    # --- 2. EXECUTION PHASE ---

    # A. Greedy Plan
    logging.info("Executing Constructive Phase: Greedy Scheduler...")
    start_greedy = time.perf_counter()
    greedy_plan = build_greedy_plan(exercises, request)
    greedy_runtime = time.perf_counter() - start_greedy
    greedy_metrics = evaluate_weekly_plan(greedy_plan, request, exercise_lookup)
    greedy_metrics["runtime"] = greedy_runtime

    # B. Random Baseline
    logging.info("Executing Baseline: Random Scheduler...")
    start_random = time.perf_counter()
    random_plan = build_random_plan(exercises, request)
    random_runtime = time.perf_counter() - start_random
    random_metrics = evaluate_weekly_plan(random_plan, request, exercise_lookup)
    random_metrics["runtime"] = random_runtime

    # C. Refinement Phase (Local Search)
    logging.info(f"Executing Refinement (Iterations: {args.iterations})...")
    start_refined = time.perf_counter()
    refined_plan, refined_metrics = refine_plan_with_replacements(
        greedy_plan, exercises, request, exercise_lookup, max_iterations=args.iterations
    )
    refined_runtime = time.perf_counter() - start_refined
    refined_metrics["runtime"] = refined_runtime

    # --- 3. DISPLAY PHASE ---

    # Print each plan in sequence
    print_schedule(greedy_plan, exercise_lookup, "Phase 1: Greedy Plan")
    print_schedule(random_plan, exercise_lookup, "Phase 2: Random Baseline")
    print_schedule(refined_plan, exercise_lookup, "Phase 3: Refined Plan (Final)")

    # Group metrics for side-by-side comparison
    comparison_data = {
        "Greedy": greedy_metrics,
        "Random": random_metrics,
        "Refined": refined_metrics
    }
    print_metrics_comparison(comparison_data)

    # --- 4. EXPORT PHASE ---
    logging.info("Saving experiment results to CSV...")
    save_results([
        ("greedy", greedy_metrics),
        ("random", random_metrics),
        ("local_search", refined_metrics)
    ])
    
    logging.info("Process Complete.")

if __name__ == "__main__":
    main()