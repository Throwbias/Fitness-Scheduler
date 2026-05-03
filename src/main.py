import argparse
import logging
import time
from src.ga.engine import GeneticSolver
from src.data_structures.models import Exercise, PlanningRequest
from src.db_connector import fetch_all_exercises
from src.utils.loader import load_request
from src.utils.printer import print_ga_schedule

def main() -> None:
    """
    Entry point for the Evolutionary Fitness Scheduler.
    Orchestrates data loading, algorithmic execution, and result display.
    """
    # 1. Configuration & CLI setup
    parser = argparse.ArgumentParser(description="Evolutionary Fitness Scheduler")
    parser.add_argument("--request", type=str, default="data/sample_request.json")
    parser.add_argument("--pop_size", type=int, default=250)
    parser.add_argument("--generations", type=int, default=200)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    logging.info("Starting Scheduler...")

    # 2. Database Integration
    # Fetches exercise library from local SQL Server via pyodbc connector
    raw_data = fetch_all_exercises()
    if not raw_data:
        logging.error("Database connection failed. Aborting.")
        return
        
    exercise_pool = [
        Exercise(
            id=str(row['ExerciseID']),
            name=row['Name'],
            category=row['CategoryName'],
            muscle_group=row['MuscleGroup'],
            difficulty=row['Difficulty'],
            duration_min=row['EstimatedTimeMins'],
            fatigue_cost=row['FatigueCost'],
            priority=row['PriorityScore'],
            min_recovery_days=row['MinRecoveryDays'],
            goal_tags=[tag.strip() for tag in row.get('GoalTags', "").split(',')] if row.get('GoalTags') else []
        ) for row in raw_data
    ]
    
    request = load_request(args.request)

    # 3. Optimization Phase
    # Runs the Genetic Algorithm to evolve the best possible weekly split.
    start_time = time.perf_counter()
    solver = GeneticSolver(request, exercise_pool, args.pop_size, args.generations)
    best_plan = solver.evolve()
    runtime = time.perf_counter() - start_time

    # 4. Reporting
    # Outputs a professionally formatted training table to the console.
    logging.info(f"Evolution complete in {runtime:.2f}s.")
    print_ga_schedule(best_plan, request)

if __name__ == "__main__":
    main()