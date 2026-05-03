import sqlite3
import os
from typing import List, Dict, Any

def get_db_connection():
    # This finds the directory where db_connector.py lives (src/)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # This moves up one level to the project root and then into data/
    db_path = os.path.join(base_dir, "..", "data", "exercise_vault.db")
    
    if not os.path.exists(db_path):
        print(f"[CRITICAL ERROR] Database file NOT found at: {db_path}")
        return None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row 
        return conn
    except Exception as e:
        print(f"[CRITICAL ERROR] Connection failed: {e}")
        return None

def fetch_all_exercises() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    query = """
        SELECT 
            e.ExerciseID, e.Name, c.CategoryName, e.MuscleGroup,
            e.Difficulty, e.EstimatedTimeMins, e.FatigueCost, 
            e.PriorityScore, e.MinRecoveryDays, e.GoalTags
        FROM Exercises e
        JOIN MovementCategories c ON e.CategoryID = c.CategoryID;
    """
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"[DB DEBUG] Successfully fetched {len(rows)} exercises from SQLite.")
        exercises = [dict(row) for row in rows]
        conn.close()
        return exercises
    except Exception as e:
        print(f"[CRITICAL ERROR] Query failed: {e}")
        return []