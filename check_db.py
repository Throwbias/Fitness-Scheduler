import sqlite3
conn = sqlite3.connect('data/exercise_vault.db')
cursor = conn.cursor()

# Check if tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(f"Tables found: {cursor.fetchall()}")

# Check row count
try:
    cursor.execute("SELECT COUNT(*) FROM Exercises")
    print(f"Rows in Exercises: {cursor.fetchone()[0]}")
except Exception as e:
    print(f"Error checking Exercises: {e}")
conn.close()