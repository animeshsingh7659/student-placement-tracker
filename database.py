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


def update_application(app_id, company, role, status, application_date, ctc):
    """Updates an existing placement application by its ID using parameterized queries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE applications
        SET company = ?, role = ?, status = ?, application_date = ?, ctc = ?
        WHERE id = ?
    """, (company.strip(), role.strip(), status, str(application_date), float(ctc), int(app_id)))
    conn.commit()
    conn.close()


def delete_application(app_id):
    """Deletes a placement application by its ID using parameterized queries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE id = ?", (int(app_id),))
    conn.commit()
    conn.close()


def get_application_by_id(app_id):
    """Fetches a single application record as a dictionary by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, company, role, status, application_date, ctc, created_at
        FROM applications
        WHERE id = ?
    """, (int(app_id),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "company": row[1],
            "role": row[2],
            "status": row[3],
            "application_date": row[4],
            "ctc": row[5],
            "created_at": row[6]
        }
    return None


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
