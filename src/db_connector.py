import pyodbc
from typing import List, Dict, Any, Optional

"""
Database Connection Layer: Handles the lifecycle of the local SQL Server connection.
Uses Windows Authentication to securely fetch exercise metadata for the 
Genetic Algorithm's initial population pool.
"""

def get_db_connection() -> Optional[pyodbc.Connection]:
    """
    Establishes a connection to the local SQL Server database.
    """
    server = r'DESKTOP-VRDBDDU\SQLEXPRESS'
    database = 'FitnessScheduler'
    conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    
    try:
        return pyodbc.connect(conn_string)
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return None

def fetch_all_exercises() -> List[Dict[str, Any]]:
    """
    Pulls the full exercise library for the GA pool. 
    Joins MovementCategories to ensure every exercise object contains 
    biomechanical taxonomy for coverage and spacing evaluations.
    """
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
    
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    
    # List comprehension for a clean dictionary mapping
    exercises = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()
    return exercises