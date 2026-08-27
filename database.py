import sqlite3
import pandas as pd

DB_NAME = "placement_tracker.db"


def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)


def init_db():
    """Initializes the database and creates the applications table if it does not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            application_date TEXT NOT NULL,
            ctc REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_application(company, role, status, application_date, ctc):
    """Inserts a new placement application into the database securely using parameterized queries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO applications (company, role, status, application_date, ctc)
        VALUES (?, ?, ?, ?, ?)
    """, (company.strip(), role.strip(), status, str(application_date), float(ctc)))
    conn.commit()
    conn.close()


def fetch_all_applications():
    """Retrieves all applications from the database as a pandas DataFrame."""
    conn = get_connection()
    query = """
        SELECT 
            id AS "ID",
            company AS "Company",
            role AS "Job Role",
            status AS "Status",
            application_date AS "Date Applied",
            ctc AS "CTC (LPA)",
            created_at AS "Created At"
        FROM applications
        ORDER BY id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
