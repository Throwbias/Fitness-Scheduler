from src.data_structures.models import Exercise, PlanningRequest, SessionPlan
from src.utils.scoring import candidate_score

def test_candidate_score_prefers_missing_category():
    ex1 = Exercise("1", "Squat", "squat", "lower", "hard", 10, 5, 8, 1)
    ex2 = Exercise("2", "Bench", "push", "upper", "moderate", 10, 5, 8, 1)

    request = PlanningRequest(
        days_available=["Mon"],
        session_time_limit=30,
        goal="strength",
        required_categories=["squat", "push"],
        daily_fatigue_cap=15,
    )

    session = SessionPlan(day="Mon")

    categories_hit = {"squat"}  # already hit squat

    score1 = candidate_score(ex1, session, request, categories_hit)
    score2 = candidate_score(ex2, session, request, categories_hit)

    assert score2 > score1  # should prefer missing category