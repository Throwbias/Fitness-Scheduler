import csv
import time

from src.algorithms.greedy_scheduler import build_greedy_plan
from src.algorithms.random_scheduler import build_random_plan
from src.algorithms.local_search import refine_plan_with_replacements
from src.utils.evaluator import evaluate_weekly_plan


def run_experiments(exercises, request, trials=30, output_path="results/raw/experiment_results.csv"):
    lookup = {ex.id: ex for ex in exercises}

    rows = []

    # Greedy baseline
    start = time.time()
    greedy_plan = build_greedy_plan(exercises, request)
    greedy_metrics = evaluate_weekly_plan(greedy_plan, request, lookup)
    greedy_time = time.time() - start

    rows.append({
        "algorithm": "greedy",
        "trial": 0,
        "runtime": greedy_time,
        **greedy_metrics
    })

    # Local search refinement
    start = time.time()
    refined_plan, refined_metrics = refine_plan_with_replacements(
        greedy_plan, exercises, request, dict(lookup)
    )
    refined_time = time.time() - start

    rows.append({
        "algorithm": "refined",
        "trial": 0,
        "runtime": refined_time,
        **refined_metrics
    })

    # Random baseline trials
    for seed in range(trials):
        start = time.time()

        plan = build_random_plan(exercises, request, seed=seed)
        metrics = evaluate_weekly_plan(plan, request, lookup)

        runtime = time.time() - start

        rows.append({
            "algorithm": "random",
            "trial": seed,
            "runtime": runtime,
            **metrics
        })

    # Write CSV
    keys = rows[0].keys()

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved results to {output_path}")