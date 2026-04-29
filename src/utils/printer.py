from src.data_structures.models import WeeklyPlan, Exercise

def print_schedule(plan: WeeklyPlan, exercise_lookup: dict[str, Exercise], title: str = "TRAINING PLAN"):
    """
    Prints a day-by-day breakdown of a specific generated workout plan, 
    now including the movement category for each exercise.
    """
    print("\n" + "="*70)
    print(f"📋 {title.upper()}")
    print("="*70)

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for day in day_order:
        session = plan.sessions.get(day)
        if not session or not session.exercise_ids:
            continue

        print(f"\n>> {day.upper()} ({session.total_time} min | {session.total_fatigue} Fatigue)")
        print("-" * 55)
        
        for ex_id in session.exercise_ids:
            ex = exercise_lookup.get(ex_id)
            if ex:
                # Column 1: Exercise Name | Column 2: Category | Column 3: Duration
                print(f"  [ ] {ex.name.ljust(25)} | {ex.category.ljust(18)} | {ex.duration_min} min")
            else:
                print(f"  [ ] Unknown ({ex_id})")

def print_metrics_comparison(all_metrics: dict[str, dict]):
    """
    Prints a side-by-side comparison table of all algorithm metrics.
    """
    headers = ["Metric", "Greedy", "Random", "Refined"]
    metrics_to_show = [
        ("Total Score", "total_score", "{:.2f}"),
        ("Fatigue Balance", "fatigue_balance_score", "{:.2f}"),
        ("Coverage", "coverage_score", "{:.2f}"),
        ("Priority Score", "priority_score", "{:.2f}"),
        ("Time Util.", "time_utilization_score", "{:.2f}"),
        ("Violations", "constraint_violations", "{:d}"),
        ("Runtime (s)", "runtime", "{:.4f}")
    ]

    print("\n" + "="*65)
    print("📊 ALGORITHM PERFORMANCE COMPARISON")
    print("="*65)
    
    header_row = f"{headers[0]:<18} | {headers[1]:>12} | {headers[2]:>12} | {headers[3]:>12}"
    print(header_row)
    print("-" * len(header_row))

    for label, key, fmt in metrics_to_show:
        greedy_val = all_metrics.get("Greedy", {}).get(key, 0)
        random_val = all_metrics.get("Random", {}).get(key, 0)
        refined_val = all_metrics.get("Refined", {}).get(key, 0)
        
        row = (f"{label:<18} | "
               f"{fmt.format(greedy_val):>12} | "
               f"{fmt.format(random_val):>12} | "
               f"{fmt.format(refined_val):>12}")
        print(row)
    
    print("="*65 + "\n")