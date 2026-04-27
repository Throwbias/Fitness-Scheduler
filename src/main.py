import argparse
import logging

from src.algorithms.greedy_scheduler import build_greedy_plan
from src.algorithms.local_search import refine_plan_with_replacements
from src.algorithms.random_scheduler import build_random_plan
from src.utils.evaluator import evaluate_weekly_plan
from src.utils.experiment_runner import save_results
from src.utils.loader import load_exercises, load_request, Exercise
from src.utils.printer import print_schedule, print_schedule_metrics
from src.db_connector import fetch_all_exercises


# Configure the logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Constraint-Based Fitness Scheduler")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/exercises_large.json",
        help="Path to the JSON file containing the exercises dataset.",
    )
    parser.add_argument(
        "--request",
        type=str,
        default="data/sample_request.json",
        help="Path to the JSON file containing the user's planning request.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Maximum number of iterations for the local search refinement.",
    )

    args = parser.parse_args()

    logging.info("Initializing Constraint-Based Fitness Scheduler...")
    logging.info(f"Using dataset: {args.dataset}")
    logging.info(f"Using request config: {args.request}")

    # --- SQL DATA PIPELINE ---
    logging.info("Connecting to SQL Server to fetch exercise library...")
    raw_exercises = fetch_all_exercises()
    
    if not raw_exercises:
        logging.error("No exercises found! Check your database connection.")
        return
        
    exercises = []
    for ex_data in raw_exercises:
        exercises.append(
            Exercise(
                id=ex_data['ExerciseID'],
                name=ex_data['Name'],
                category=ex_data['CategoryName'],
                is_heavy_compound=bool(ex_data['IsHeavyCompound']),
                priority_score=ex_data['PriorityScore'],
                fatigue_cost=ex_data['FatigueCost'],
                estimated_time=ex_data['EstimatedTimeMins']
            )
        )
    
    logging.info(f"Successfully loaded {len(exercises)} exercises into the engine.")
    exercise_lookup = {ex.id: ex for ex in exercises}
    request = load_request(args.request)

    # 1. Greedy Plan
    logging.info("Executing Constructive Phase: Greedy Scheduler...")
    greedy_plan = build_greedy_plan(exercises, request)
    greedy_metrics = evaluate_weekly_plan(greedy_plan, request, exercise_lookup)
    logging.info(
        f"Greedy plan constructed with score: {greedy_metrics['total_score']:.3f}"
    )

    # 2. Random Baseline
    logging.info("Executing Baseline: Random Scheduler...")
    random_plan = build_random_plan(exercises, request)
    random_metrics = evaluate_weekly_plan(random_plan, request, exercise_lookup)
    logging.info(
        f"Random plan constructed with score: {random_metrics['total_score']:.3f}"
    )

    # 3. Refined Plan
    logging.info(
        f"Executing Refinement Phase: Local Search (Max Iterations: {args.iterations})..."
    )
    refined_plan, refined_metrics = refine_plan_with_replacements(
        greedy_plan, exercises, request, exercise_lookup, max_iterations=args.iterations
    )
    logging.info(
        f"Refined plan optimized with score: {refined_metrics['total_score']:.3f}"
    )
    #Delegate the printing to printer.py
    print_schedule_metrics(refined_metrics)

    # Save Results
    logging.info("Saving experiment results to CSV...")
    save_results(
        [
            {"algorithm": "greedy", **greedy_metrics},
            {"algorithm": "random", **random_metrics},
            {"algorithm": "refined", **refined_metrics},
        ]
    )
    # Print the actual schedule to the terminal
    print_schedule(refined_plan, exercise_lookup)
    logging.info("Execution complete.")


if __name__ == "__main__":
    main()
