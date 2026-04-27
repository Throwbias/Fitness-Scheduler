def print_schedule(plan, exercise_lookup):
    """
    Prints the weekly workout plan in chronological order.
    Correctly matches the attributes in src/data_structures/models.py.
    """
    print("\n" + "=" * 50)
    print("🏋️  FINAL OPTIMIZED WEEKLY SCHEDULE  🏋️")
    print("=" * 50)

    # Define the chronological order for the week
    chrono_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    # Sort the dictionary items based on their position in the chrono_order list
    sorted_sessions = sorted(
        plan.sessions.items(),
        key=lambda x: chrono_order.index(x[0]) if x[0] in chrono_order else 99,
    )

    for day, session in sorted_sessions:
        print(f"\n📅 Day {day}:")

        if not session.exercise_ids:
            print("   [Rest Day]")
            continue

        print(
            f"   ⏱️ Total Time: {session.total_time} mins | 🔋 Total Fatigue: {session.total_fatigue}"
        )
        print("   Exercises:")

        for i, ex_id in enumerate(session.exercise_ids, 1):
            ex = exercise_lookup[ex_id]
            print(
                f"     {i}. {ex.name} ({ex.category}) - {ex.duration_min}m / {ex.fatigue_cost}f"
            )

    print("\n" + "=" * 50 + "\n")

def print_schedule_metrics(metrics: dict):
    """
    Prints a formatted summary of the evaluation metrics.
    """
    print("\n" + "="*40)
    print("🏆 FINAL SCHEDULE METRICS")
    print("="*40)
    print(f"Total Score:           {metrics.get('total_score', 0):.2f}")
    print(f"Fatigue Balance (Var): {metrics.get('fatigue_variance', 0):.2f} (Lower is better)")
    print(f"Coverage Score:        {metrics.get('coverage_score', 0):.2f}")
    print(f"Priority Score:        {metrics.get('priority_score', 0):.2f}")
    print(f"Time Utilization:      {metrics.get('time_utilization', 0):.2f}")
    print(f"Constraint Violations: {metrics.get('constraint_violations', 0)}")
    print("="*40 + "\n")