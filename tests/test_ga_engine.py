import pytest
from src.ga.engine import GeneticSolver
from src.data_structures.models import Exercise, PlanningRequest

# --- FIXTURES (Setup Data for Tests) ---

@pytest.fixture
def sample_exercise_pool():
    """A tiny, in-memory exercise database for fast testing."""
    return [
        Exercise(id="1", name="Squat", category="Knee Dominant", muscle_group="Legs", difficulty=3, duration_min=10, fatigue_cost=8, priority=10, min_recovery_days=2, goal_tags=[]),
        Exercise(id="2", name="Bench Press", category="Horizontal Push", muscle_group="Chest", difficulty=3, duration_min=10, fatigue_cost=7, priority=10, min_recovery_days=2, goal_tags=[]),
        Exercise(id="3", name="Pull Up", category="Vertical Pull", muscle_group="Back", difficulty=4, duration_min=8, fatigue_cost=6, priority=9, min_recovery_days=1, goal_tags=[])
    ]

@pytest.fixture
def sample_request():
    """A basic user request."""
    return PlanningRequest(
        days_available=[0, 2, 4],
        session_time_limit=60,
        goal="Hypertrophy",
        required_categories=["Knee Dominant", "Horizontal Push"],
        daily_fatigue_cap=80,
        max_exercises_per_session=2,
        desired_training_days_per_week=3
    )

# --- TESTS ---

def test_solver_initialization(sample_request, sample_exercise_pool):
    """Ensure the engine absorbs parameters correctly."""
    solver = GeneticSolver(sample_request, sample_exercise_pool, pop_size=20, generations=10)
    
    # Check that variables mapped correctly to the instance
    assert solver.pop_size == 20
    assert solver.generations == 10
    assert len(solver.exercise_pool) == 3

def test_solver_evolution_execution(sample_request, sample_exercise_pool):
    """Ensure the evolve process can run start-to-finish without crashing."""
    # We use a very small pop_size and generation count so the test is instant
    solver = GeneticSolver(sample_request, sample_exercise_pool, pop_size=10, generations=2)
    best_plan = solver.evolve()
    
    # We don't care about the exact score here, just that it returns a scored plan
    assert hasattr(best_plan, 'fitness_score')
    assert isinstance(best_plan.fitness_score, float)