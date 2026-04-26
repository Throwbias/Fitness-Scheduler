import argparse
import logging

from src.algorithms.greedy_scheduler import build_greedy_plan
from src.algorithms.local_search import refine_plan_with_replacements
from src.algorithms.random_scheduler import build_random_plan
from src.utils.evaluator import evaluate_weekly_plan
from src.utils.experiment_runner import save_results
from src.utils.loader import load_exercises, load_request
from src.utils.printer import print_schedule

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

    exercises = load_exercises(args.dataset)
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
