import sqlite3
import pandas as pd

DB_NAME = "placement_tracker.db"


def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME, timeout=10)


def _validate_application_inputs(company, role, application_date, ctc):
    """
    Helper function to validate and clean common application inputs.
    Ensures text fields are non-empty and numbers are valid.
    """
    company_clean = company.strip() if company else ""
    role_clean = role.strip() if role else ""

    if not company_clean:
        raise ValueError("Company name cannot be empty or contain only whitespace.")
    if not role_clean:
        raise ValueError("Job role cannot be empty or contain only whitespace.")
    if ctc is None or float(ctc) < 0:
        raise ValueError("CTC / Package must be a non-negative number.")
    if not application_date:
        raise ValueError("Application date is required.")

    return company_clean, role_clean, str(application_date), float(ctc)


def init_db():
    """Initializes the database and creates the applications table if it does not exist."""
    conn = None
    try:
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
    except sqlite3.Error as e:
        raise RuntimeError(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()


def add_application(company, role, status, application_date, ctc):
    """Inserts a new placement application into the database securely using parameterized queries."""
    company_clean, role_clean, date_str, ctc_val = _validate_application_inputs(
        company, role, application_date, ctc
    )

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications (company, role, status, application_date, ctc)
            VALUES (?, ?, ?, ?, ?)
        """, (company_clean, role_clean, status, date_str, ctc_val))
        conn.commit()
        return True
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error while adding application: {e}")
    finally:
        if conn:
            conn.close()


def update_application(app_id, company, role, status, application_date, ctc):
    """Updates an existing placement application by its ID using parameterized queries."""
    if not app_id:
        raise ValueError("Invalid application ID.")

    company_clean, role_clean, date_str, ctc_val = _validate_application_inputs(
        company, role, application_date, ctc
    )

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE applications
            SET company = ?, role = ?, status = ?, application_date = ?, ctc = ?
            WHERE id = ?
        """, (company_clean, role_clean, status, date_str, ctc_val, int(app_id)))
        conn.commit()
        return True
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error while updating application: {e}")
    finally:
        if conn:
            conn.close()


def delete_application(app_id):
    """Deletes a placement application by its ID using parameterized queries."""
    if not app_id:
        raise ValueError("Invalid application ID.")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM applications WHERE id = ?", (int(app_id),))
        conn.commit()
        return True
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error while deleting application: {e}")
    finally:
        if conn:
            conn.close()


def get_application_by_id(app_id):
    """Fetches a single application record as a dictionary by its ID."""
    if not app_id:
        return None

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, company, role, status, application_date, ctc, created_at
            FROM applications
            WHERE id = ?
        """, (int(app_id),))
        row = cursor.fetchone()
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
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error while fetching application: {e}")
    finally:
        if conn:
            conn.close()


def fetch_all_applications():
    """Retrieves all applications from the database as a pandas DataFrame."""
    conn = None
    try:
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
        return df
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error while retrieving applications: {e}")
    finally:
        if conn:
            conn.close()


def get_application_metrics():
    """Calculates summary counts for total and status-specific applications dynamically from SQLite."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Applied' THEN 1 ELSE 0 END) AS applied,
                SUM(CASE WHEN status = 'Shortlisted' THEN 1 ELSE 0 END) AS shortlisted,
                SUM(CASE WHEN status = 'Interview' THEN 1 ELSE 0 END) AS interview,
                SUM(CASE WHEN status = 'Selected' THEN 1 ELSE 0 END) AS selected,
                SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) AS rejected
            FROM applications
        """)
        row = cursor.fetchone()
        return {
            "total": row[0] if row and row[0] is not None else 0,
            "applied": row[1] if row and row[1] is not None else 0,
            "shortlisted": row[2] if row and row[2] is not None else 0,
            "interview": row[3] if row and row[3] is not None else 0,
            "selected": row[4] if row and row[4] is not None else 0,
            "rejected": row[5] if row and row[5] is not None else 0
        }
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error while calculating metrics: {e}")
    finally:
        if conn:
            conn.close()
