import logging
from typing import Dict, List
from src.data_structures.models import Individual, PlanningRequest

def print_ga_schedule(individual: Individual, request: PlanningRequest):
    """
    Prints the evolved 7-day workout plan in a clean, professional format.
    Maps day indices (0-6) to their names and calculates session totals.
    """
    DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    
    print("\n" + "="*60)
    print(f"{'FINAL EVOLVED WORKOUT PLAN':^60}")
    print(f"{f'Fitness Score: {individual.fitness_score:.2f}':^60}")
    print("="*60)

    for i, day_name in enumerate(DAYS):
        session = individual.chromosome[i]
        
        # Determine if this was a requested training day
        is_training_day = i in request.days_available
        
        if not is_training_day:
            # Skip printing days that weren't requested as training days
            continue
            
        print(f"\n[ {day_name} ]")
        
        if not session:
            print("  (No exercises scheduled for this available slot)")
            continue
            
        total_time = sum(ex.duration_min for ex in session)
        total_fatigue = sum(ex.fatigue_cost for ex in session)
        
        # Header for the exercise list
        print(f"  {'Exercise':<22} | {'Time':<7} | {'Category':<18}")
        print(f"  {'-'*22}-|-{'-'*7}-|-{'-'*18}")
        
        for ex in session:
            print(f"  {ex.name[:22]:<22} | {ex.duration_min:<3} min | {ex.category:<18}")
            
        print(f"  {'-'*55}")
        print(f"  >> Session Totals: {total_time} / {request.session_time_limit} min | "
              f"Fatigue: {total_fatigue} / {request.daily_fatigue_cap}")

    print("\n" + "="*60)
    print(f"{'End of Schedule':^60}")
    print("="*60 + "\n")

def print_metrics_comparison(comparison_data: Dict[str, Dict]):
    """
    Optional: Keeps compatibility if you want to compare different GA runs later.
    """
    print("\n" + "="*40)
    print(f"{'ALGORITHM PERFORMANCE COMPARISON':^40}")
    print("="*40)
    for algo, metrics in comparison_data.items():
        print(f"\n[{algo}]")
        for metric, value in metrics.items():
            if isinstance(value, float):
                print(f"  {metric:<20}: {value:>8.2f}")
            else:
                print(f"  {metric:<20}: {value:>8}")
    print("="*40 + "\n")