import pyodbc

def get_db_connection():
    """
    Establishes a connection to the local SQL Server database.
    """
    server = r'DESKTOP-VRDBDDU\SQLEXPRESS'
    database = 'FitnessScheduler'

    # Windows Authentication remains the standard
    conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    
    try:
        conn = pyodbc.connect(conn_string)
        return conn
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return None

def fetch_all_exercises():
    """
    Pulls the full exercise library for the GA pool.
    """
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    
    # We fetch all metadata required for the Spacing and Recovery logic
    query = """
        SELECT 
            e.ExerciseID, 
            e.Name, 
            c.CategoryName, 
            e.MuscleGroup,
            e.Difficulty,
            e.EstimatedTimeMins,
            e.FatigueCost, 
            e.PriorityScore,
            e.MinRecoveryDays,
            e.GoalTags
        FROM Exercises e
        JOIN MovementCategories c ON e.CategoryID = c.CategoryID;
    """
    
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    
    exercises = []
    for row in cursor.fetchall():
        exercises.append(dict(zip(columns, row)))

    conn.close()
    return exercises