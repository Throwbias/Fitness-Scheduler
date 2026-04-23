from src.data_structures.models import Exercise, PlanningRequest, SessionPlan
from src.utils.filters import fits_time, fits_fatigue, has_recovery_conflict

def test_fits_time_true():
    ex = Exercise("1", "Test", "push", "upper", "easy", 10, 3, 5, 1)
    req = PlanningRequest(["Mon"], 30, "strength", ["push"], 10)
    session = SessionPlan(day="Mon", total_time=15)
    assert fits_time(ex, session, req) is True


def test_fits_time_false():
    ex = Exercise("1", "Test", "push", "upper", "easy", 20, 3, 5, 1)
    req = PlanningRequest(["Mon"], 30, "strength", ["push"], 10)
    session = SessionPlan(day="Mon", total_time=15)
    assert fits_time(ex, session, req) is False


def test_fits_fatigue_true():
    ex = Exercise("1", "Test", "push", "upper", "easy", 10, 2, 5, 1)
    req = PlanningRequest(["Mon"], 30, "strength", ["push"], 10)
    session = SessionPlan(day="Mon", total_fatigue=7)
    assert fits_fatigue(ex, session, req) is True


def test_fits_fatigue_false():
    ex = Exercise("1", "Test", "push", "upper", "easy", 10, 3, 5, 1)
    req = PlanningRequest(["Mon"], 30, "strength", ["push"], 10)
    session = SessionPlan(day="Mon", total_fatigue=8)
    assert fits_fatigue(ex, session, req) is False


def test_recovery_conflict_true():
    ex = Exercise("1", "Back Squat", "squat", "lower", "hard", 12, 8, 9, 2)
    last_day_by_category = {"squat": 0}
    assert has_recovery_conflict(ex, 1, last_day_by_category) is True


def test_recovery_conflict_false():
    ex = Exercise("1", "Back Squat", "squat", "lower", "hard", 12, 8, 9, 2)
    last_day_by_category = {"squat": 0}
    assert has_recovery_conflict(ex, 2, last_day_by_category) is False