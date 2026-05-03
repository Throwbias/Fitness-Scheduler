import pyodbc
import sqlite3
import os

# CONFIG
SERVER = r'DESKTOP-VRDBDDU\SQLEXPRESS'
DATABASE = 'FitnessScheduler'
SQL_CONN_STR = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
SQLITE_DB_PATH = 'data/exercise_vault.db'

def migrate():
    try:
        # 1. Pull from SQL Server
        print("Reading from SQL Server...")
        sql_conn = pyodbc.connect(SQL_CONN_STR)
        sql_cursor = sql_conn.cursor()
        
        sql_cursor.execute("SELECT CategoryID, CategoryName FROM MovementCategories")
        cats = [tuple(r) for r in sql_cursor.fetchall()]
        
        sql_cursor.execute("""
            SELECT ExerciseID, Name, CategoryID, MuscleGroup, Difficulty, 
                   EstimatedTimeMins, FatigueCost, PriorityScore, MinRecoveryDays, GoalTags 
            FROM Exercises
        """)
        exs = [tuple(x if x is not None else "" for x in r[:10]) for r in sql_cursor.fetchall()]
        sql_conn.close()

        print(f"Captured {len(cats)} categories and {len(exs)} exercises from SQL Server.")

        # 2. Write to SQLite
        if os.path.exists(SQLITE_DB_PATH):
            os.remove(SQLITE_DB_PATH) # Delete old empty DB to start fresh
            
        lite_conn = sqlite3.connect(SQLITE_DB_PATH)
        lite_cursor = lite_conn.cursor()

        lite_cursor.execute("CREATE TABLE MovementCategories (CategoryID INT, CategoryName TEXT)")
        lite_cursor.execute("""
            CREATE TABLE Exercises (
                ExerciseID INT, Name TEXT, CategoryID INT, MuscleGroup TEXT,
                Difficulty TEXT, EstimatedTimeMins INT, FatigueCost INT, 
                PriorityScore INT, MinRecoveryDays INT, GoalTags TEXT
            )
        """)

        lite_cursor.executemany("INSERT INTO MovementCategories VALUES (?,?)", cats)
        lite_cursor.executemany("INSERT INTO Exercises VALUES (?,?,?,?,?,?,?,?,?,?)", exs)

        # CRITICAL: Save and Force Write
        lite_conn.commit()
        
        # Verify immediately
        lite_cursor.execute("SELECT COUNT(*) FROM Exercises")
        check_count = lite_cursor.fetchone()[0]
        lite_conn.close()

        print(f"Migration Successful! SQLite now contains {check_count} exercises.")

    except Exception as e:
        print(f"[FATAL ERROR] {e}")

if __name__ == "__main__":
    migrate()