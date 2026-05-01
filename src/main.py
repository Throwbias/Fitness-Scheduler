import argparse
import logging
import time
from typing import List

# Genetic Algorithm Core
from src.ga.engine import GeneticSolver
from src.ga.evaluator import GAEvaluator

# Utilities and Data Structures
from src.data_structures.models import Exercise, PlanningRequest
from src.db_connector import fetch_all_exercises
from src.utils.loader import load_request
from src.utils.printer import print_ga_schedule # Note: We will update this utility next

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    parser = argparse.ArgumentParser(description="Evolutionary Fitness Scheduler")
    parser.add_argument("--request", type=str, default="data/sample_request.json")
    parser.add_argument("--pop_size", type=int, default=100)
    parser.add_argument("--generations", type=int, default=150)
    args = parser.parse_args()

    logging.info("Initializing Evolutionary Fitness Scheduler...")

    # --- 1. DATA LOADING PHASE ---
    # We maintain your existing connection to SQL Server via pyodbc
    logging.info("Connecting to SQL Server to fetch exercise library...")
    raw_exercises = fetch_all_exercises()
    
    if not raw_exercises:
        logging.error("No exercises found! Check your SQL Server connection.")
        return
        
    # Map SQL rows to the Exercise dataclass used by the GA
    exercises = []
    for ex_data in raw_exercises:
        raw_tags = ex_data.get('GoalTags', "")
        tags_list = [tag.strip() for tag in raw_tags.split(',')] if raw_tags else []
        exercises.append(
            Exercise(
                id=str(ex_data['ExerciseID']),
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
    request = load_request(args.request)

    # --- 2. EVOLUTIONARY PHASE ---
    logging.info(f"Starting Evolution (Population: {args.pop_size}, Generations: {args.generations})...")
    
    start_time = time.perf_counter()
    
    # Initialize the Engine
    solver = GeneticSolver(
        request=request, 
        exercise_pool=exercises, 
        pop_size=args.pop_size,
        generations=args.generations
    )
    
    # Run the solver to find the optimal 7-day chromosome
    best_plan = solver.evolve()
    
    runtime = time.perf_counter() - start_time
    logging.info(f"Evolution complete in {runtime:.2f} seconds.")

    # --- 3. DISPLAY PHASE ---
    # We use a specialized printer to handle the 7-day chromosome structure
    print_ga_schedule(best_plan, request)

    logging.info("Process Complete.")

if __name__ == "__main__":
    main()