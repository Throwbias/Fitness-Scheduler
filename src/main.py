from src.utils.loader import load_exercises, load_request
from src.algorithms.greedy_scheduler import build_greedy_plan
from src.algorithms.random_scheduler import build_random_plan
from src.algorithms.local_search import refine_plan_with_replacements
from src.utils.evaluator import evaluate_weekly_plan
from src.utils.experiment_runner import run_experiments

DATASET_PATH = "data/exercises_large.json"
REQUEST_PATH = "data/sample_request.json"

def print_plan(title, plan, exercise_lookup, metrics):
    print(f"\n{title}")
    print("=" * 40)

    for day, session in plan.sessions.items():
        print(f"\n{day}")
        for ex_id in session.exercise_ids:
            ex = exercise_lookup[ex_id]
            print(f"  - {ex.name} ({ex.category}, {ex.duration_min} min)")
        print(f"  Total time: {session.total_time}")
        print(f"  Total fatigue: {session.total_fatigue}")

    print("\nMETRICS")
    print("-" * 40)
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")


def print_comparison(greedy_metrics, random_metrics, refined_metrics):
    print("\nCOMPARISON")
    print("=" * 40)
    for key in greedy_metrics:
        g = greedy_metrics[key]
        r = random_metrics[key]
        ref = refined_metrics[key]

        if isinstance(g, float):
            print(f"{key}: greedy={g:.3f} | random={r:.3f} | refined={ref:.3f}")
        else:
            print(f"{key}: greedy={g} | random={r} | refined={ref}")


def main():

    exercises = load_exercises("data/exercises.json")
    request = load_request("data/sample_request.json")

    exercise_lookup = {ex.id: ex for ex in exercises}

    greedy_plan = build_greedy_plan(exercises, request)
    greedy_metrics = evaluate_weekly_plan(greedy_plan, request, exercise_lookup)

    random_plan = build_random_plan(exercises, request, seed=42)
    random_metrics = evaluate_weekly_plan(random_plan, request, exercise_lookup)

    refined_plan, refined_metrics = refine_plan_with_replacements(
        greedy_plan, exercises, request, dict(exercise_lookup)
    )

    print_plan("GREEDY PLAN", greedy_plan, exercise_lookup, greedy_metrics)
    print_plan("RANDOM BASELINE PLAN", random_plan, exercise_lookup, random_metrics)
    print_plan("REFINED PLAN", refined_plan, exercise_lookup, refined_metrics)

    print_comparison(greedy_metrics, random_metrics, refined_metrics)
    run_experiments(exercises, request, trials=30)


if __name__ == "__main__":
    main()
    