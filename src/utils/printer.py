from typing import Dict, List
from src.data_structures.models import Individual, PlanningRequest

"""
Output visualizer: Responsible for translating the evolved 7-day chromosome 
into a professional, console-based training table.
"""

def print_ga_schedule(individual: Individual, request: PlanningRequest) -> None:
    """
    Maps day indices (0-6) to their names and calculates session totals 
    to verify that constraints (Time/Fatigue) were respected.
    """
    DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    
    print("\n" + "="*60)
    print(f"{'FINAL EVOLVED WORKOUT PLAN':^60}")
    print(f"{f'Fitness Score: {individual.fitness_score:.2f}':^60}")
    print("="*60)

    for i, day_name in enumerate(DAYS):
        # Determine if this was a requested training day
        if i not in request.days_available:
            continue
            
        session = individual.chromosome[i]
        print(f"\n[ {day_name} ]")
        
        if not session:
            print("  (No exercises scheduled for this available slot)")
            continue
            
        total_time = sum(ex.duration_min for ex in session)
        total_fatigue = sum(ex.fatigue_cost for ex in session)
        
        # Table Header
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