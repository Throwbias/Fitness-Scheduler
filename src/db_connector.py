import pyodbc

def get_db_connection():
    """
    Establishes a connection to the local SQL Server database.
    """
    # NOTE: You will need to change 'YOUR_SERVER_NAME' to what shows up 
    # at the very top of your Object Explorer in SSMS (e.g., 'localhost\SQLEXPRESS' or just '.')
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
    Pulls the exercises from SQYOURL and formats them as a list of dictionaries.
    """
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor()
    
    # We use a JOIN to grab the actual Category Name instead of just the ID
    query = """
        SELECT 
            e.ExerciseID, 
            e.Name, 
            c.CategoryName, 
            e.IsHeavyCompound, 
            e.PriorityScore, 
            e.FatigueCost, 
            e.EstimatedTimeMins
        FROM Exercises e
        JOIN MovementCategories c ON e.CategoryID = c.CategoryID;
    """
    
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    
    exercises = []
    for row in cursor.fetchall():
        # Zip combines the column names with the row values into a dictionary
        exercise_dict = dict(zip(columns, row))
        exercises.append(exercise_dict)

    conn.close()
    return exercises

# --- Quick Test ---
if __name__ == "__main__":
    ex_list = fetch_all_exercises()
    print(f"Loaded {len(ex_list)} exercises from the database.")
    if ex_list:
        print("First exercise looks like this:")
        print(ex_list[0])