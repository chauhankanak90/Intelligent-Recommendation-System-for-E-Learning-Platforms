# database.py
import sqlite3
import os

DB_PATH = "data/students.db"


def get_db_connection():
    """Database se connect karne ke liye helper function."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Database tables create karne ke liye function."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Students Table: Student ki profile save karne ke liye
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        year TEXT,
        branch TEXT,
        skills TEXT,
        goal TEXT,
        level TEXT,
        study_time INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Roadmaps Table: analysis_json = Strengths/Weaknesses/Missing Skills,
    #    roadmap_json = 12-Week Roadmap plan (both stored as JSON text)
    # NOTE: SQLite only understands "--" comments, NOT "#" — a "#" inside this
    # string used to throw "OperationalError: near '#': syntax error" on first run.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roadmaps (
        student_id INTEGER PRIMARY KEY,
        analysis_json TEXT,
        roadmap_json TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    """)

    # 3. Quiz Scores Table: Quizzes ke results track karne ke liye
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        topic TEXT,
        score INTEGER,
        total INTEGER,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    """)

    # 4. Week Progress Table: roadmap ke har week ko complete mark karne ke liye
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS week_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        week_label TEXT,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    """)

    conn.commit()
    _migrate_schema(conn)
    conn.close()


def _migrate_schema(conn):
    """Agar students.db pehle se (purane schema ke sath) exist karti thi,
    'CREATE TABLE IF NOT EXISTS' usse upgrade nahi karta — isliye yahan
    missing columns ko safely ALTER TABLE se add kiya jaata hai."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(roadmaps)")
    existing_cols = {row[1] for row in cursor.fetchall()}

    if "updated_at" not in existing_cols:
        cursor.execute("ALTER TABLE roadmaps ADD COLUMN updated_at TIMESTAMP")

    # Purani roadmaps table mein student_id UNIQUE/PRIMARY KEY nahi tha, isliye
    # ON CONFLICT(student_id) wala upsert fail ho sakta hai. Duplicate rows
    # (agar ho) hata kar ek unique index bana dete hain taaki upsert kaam kare.
    cursor.execute("""
        DELETE FROM roadmaps
        WHERE rowid NOT IN (
            SELECT MIN(rowid) FROM roadmaps GROUP BY student_id
        )
    """)
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_roadmaps_student ON roadmaps(student_id)")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_week_progress ON week_progress(student_id, week_label)")
    conn.commit()


def save_student_profile(name, year, branch, skills, goal, level, study_time):
    """Naye student ki profile database mein save ya update karta hai."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM students WHERE name = ?", (name,))
    row = cursor.fetchone()

    if row:
        student_id = row["id"]
        cursor.execute("""
        UPDATE students
        SET year=?, branch=?, skills=?, goal=?, level=?, study_time=?
        WHERE id=?
        """, (year, branch, skills, goal, level, study_time, student_id))
    else:
        cursor.execute("""
        INSERT INTO students (name, year, branch, skills, goal, level, study_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, year, branch, skills, goal, level, study_time))
        student_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return student_id


def save_roadmap(student_id, analysis_json, roadmap_json):
    """Roadmap aur Profile Analysis ko database mein save/update karta hai."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO roadmaps (student_id, analysis_json, roadmap_json, updated_at)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(student_id) DO UPDATE SET
        analysis_json = excluded.analysis_json,
        roadmap_json = excluded.roadmap_json,
        updated_at = CURRENT_TIMESTAMP
    """, (student_id, analysis_json, roadmap_json))
    conn.commit()
    conn.close()


def toggle_week_progress(student_id, week_label, completed: bool):
    """Ek roadmap week ko complete/incomplete mark karta hai (checkbox se call hota hai)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO week_progress (student_id, week_label, completed)
    VALUES (?, ?, ?)
    ON CONFLICT(student_id, week_label) DO UPDATE SET completed = excluded.completed
    """, (student_id, week_label, int(completed)))
    conn.commit()
    conn.close()


def get_week_progress(student_id) -> dict:
    """Student ke roadmap progress ko {week_label: True/False} dict mein return karta hai."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT week_label, completed FROM week_progress WHERE student_id = ?", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row["week_label"]: bool(row["completed"]) for row in rows}


def save_quiz_score(student_id, topic, score, total):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO quiz_scores (student_id, topic, score, total)
    VALUES (?, ?, ?, ?)
    """, (student_id, topic, score, total))
    conn.commit()
    conn.close()


def get_quiz_history(student_id, limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT topic, score, total, date FROM quiz_scores
    WHERE student_id = ? ORDER BY date DESC LIMIT ?
    """, (student_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_data(name):
    """Student ki complete profile aur roadmap fetch karne ke liye."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.*, r.analysis_json, r.roadmap_json
    FROM students s
    LEFT JOIN roadmaps r ON s.id = r.student_id
    WHERE s.name = ?
    """, (name,))
    data = cursor.fetchone()
    conn.close()
    return dict(data) if data else None


if __name__ == "__main__":
    init_db()
    print("Database Tables Successfully Created!")