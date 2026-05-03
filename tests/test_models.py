from src.data_structures.models import Exercise, PlanningRequest

def test_exercise_creation():
    """Verify that the Exercise model accepts and stores data correctly."""
    ex = Exercise(
        id="101", 
        name="Barbell Squat", 
        category="Knee Dominant",
        muscle_group="Legs", 
        difficulty=3, 
        duration_min=12,
        fatigue_cost=8, 
        priority=10, 
        min_recovery_days=2, 
        goal_tags=["Hypertrophy", "Strength"]
    )
    
    assert ex.name == "Barbell Squat"
    assert ex.fatigue_cost == 8
    assert "Strength" in ex.goal_tags

def test_planning_request_creation():
    """Verify that the user's Planning Request handles constraints properly."""
    req = PlanningRequest(
        days_available=[0, 2, 4], # Mon, Wed, Fri
        session_time_limit=60,
        goal="Hypertrophy",
        required_categories=["Knee Dominant", "Horizontal Push"],
        daily_fatigue_cap=80,
        max_exercises_per_session=6,
        desired_training_days_per_week=3
    )
    
    assert req.session_time_limit == 60
    assert len(req.days_available) == 3
    assert req.goal == "Hypertrophy"