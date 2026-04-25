def print_schedule(plan, exercise_lookup):
    """Prints the weekly workout plan in a clean, readable format."""
    print("\n" + "="*50)
    print("🏋️  FINAL OPTIMIZED WEEKLY SCHEDULE  🏋️")
    print("="*50)
    
    # Sort the days so they print in order
    for day, session in sorted(plan.sessions.items()):
        print(f"\n📅 Day {day}:")
        
        # Check if it's a rest day 
        if not session.exercise_ids:
            print("   [Rest Day]")
            continue
            
        # Print session stats (FIX: changed total_time_minutes to total_time)
        print(f"   ⏱️ Total Time: {session.total_time} mins | 🔋 Total Fatigue: {session.total_fatigue}")
        print("   Exercises:")
        
        # Print each exercise by looking up its ID
        for i, ex_id in enumerate(session.exercise_ids, 1):
            ex = exercise_lookup[ex_id]
            print(f"     {i}. {ex.name} ({ex.category}) - {ex.time_cost}m / {ex.fatigue_cost}f")
            
    print("\n" + "="*50 + "\n")