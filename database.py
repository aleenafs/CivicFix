# database.py
# MODULE 2: Handles all database operations
# Anything that reads or writes to the database lives here.
# This way if we ever change our database, we only change this file.

import sqlite3
import os

DB_PATH = 'civicfix.db'

def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn

def init_db():
    """Create the reports table if it doesn't exist yet.
    Called once when the app starts up."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            issue_type          TEXT NOT NULL,
            description         TEXT,
            location            TEXT,
            priority            TEXT,
            status              TEXT DEFAULT 'pending',
            photo_path          TEXT,
            trust_score         REAL DEFAULT 5.0,
            verification_count  INTEGER DEFAULT 0,
            votes               INTEGER DEFAULT 0,
            submitted_at        TEXT,
            ward                TEXT,
            department          TEXT,
            lat                 REAL,
            lng                 REAL,
            severity_score      REAL DEFAULT 0.0,
            predicted_worsening TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_report(issue_type, description, location, priority,
                  photo_path, submitted_at, ward, department,
                  severity_score=0.0, predicted_worsening='Stable'):
    """Insert a new report into the database. Returns the new report's ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO reports
        (issue_type, description, location, priority, photo_path,
         submitted_at, ward, department, severity_score, predicted_worsening)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (issue_type, description, location, priority, photo_path,
          submitted_at, ward, department, severity_score, predicted_worsening))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_all_reports():
    """Fetch all reports, newest first."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM reports ORDER BY submitted_at DESC')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats():
    """Return summary statistics for the dashboard."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM reports')
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM reports WHERE status='resolved'")
    resolved = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM reports WHERE status='pending'")
    pending = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM reports WHERE priority='HIGH'")
    high_priority = c.fetchone()[0]
    conn.close()
    return {
        'total': total,
        'resolved': resolved,
        'pending': pending,
        'high_priority': high_priority
    }

def get_reports_by_ward():
    """Return report counts grouped by ward — used for heat map clustering."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT ward, COUNT(*) as count,
               SUM(CASE WHEN priority='HIGH' THEN 1 ELSE 0 END) as high_count
        FROM reports
        GROUP BY ward
        ORDER BY count DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_verification(report_id, new_trust_score):
    """Update a report's verification count and trust score."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE reports
        SET verification_count = verification_count + 1,
            trust_score = ?
        WHERE id = ?
    ''', (new_trust_score, report_id))
    conn.commit()
    conn.close()