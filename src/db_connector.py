import pyodbc

def get_db_connection():
    """
    Establishes a connection to the local SQL Server database.
    """
    server = r'DESKTOP-VRDBDDU\SQLEXPRESS'
    database = 'FitnessScheduler'

    # Using Windows Authentication (Trusted_Connection=yes)
    conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    
    try:
        conn = pyodbc.connect(conn_string)
        print("[SUCCESS] Connected to SQL Server!")
        return conn
    except Exception as e:
        print(f"[ERROR] Could not connect to database: {e}")
        return None

def fetch_all_exercises():
    """
    Pulls the exercises from SQL and formats them as a list of dictionaries.
    """
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    
    # Expanded query to include MuscleGroup, Difficulty, and MinRecoveryDays
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
        exercise_dict = dict(zip(columns, row))
        exercises.append(exercise_dict)

    conn.close()
    return exercises