import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime
from app.config import DB_PATH

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def db_session():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with db_session() as conn:
        cursor = conn.cursor()
        
        # Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            current_streak INTEGER DEFAULT 1,
            total_study_time INTEGER DEFAULT 0,
            last_active_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Study Materials Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            extracted_text TEXT,
            analysis_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # Topics Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            description TEXT,
            material_id INTEGER,
            difficulty_level TEXT DEFAULT 'intermediate',
            concepts_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (material_id) REFERENCES study_materials(id) ON DELETE SET NULL
        )
        """)
        
        # Learning Sessions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            current_concept_index INTEGER DEFAULT 0,
            current_difficulty TEXT DEFAULT 'Medium',
            current_teaching_style TEXT DEFAULT 'Standard',
            current_cognitive_load TEXT DEFAULT 'MEDIUM',
            consecutive_high_load_count INTEGER DEFAULT 0,
            is_completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
        )
        """)
        
        # Interaction Logs Table (Measurable learning-behavior signals)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interaction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            concept_id TEXT NOT NULL,
            concept_title TEXT,
            question_id TEXT NOT NULL,
            question_difficulty TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            response_time_seconds REAL NOT NULL,
            attempts INTEGER NOT NULL,
            hints_used INTEGER NOT NULL,
            skipped BOOLEAN DEFAULT 0,
            repeated_mistakes INTEGER DEFAULT 0,
            time_since_last_action REAL DEFAULT 0,
            predicted_cognitive_load TEXT NOT NULL,
            load_probability_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES learning_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # Mastery Records Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mastery_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            session_id INTEGER,
            mastery_score REAL NOT NULL,
            is_mastered BOOLEAN NOT NULL,
            mastered_concepts_json TEXT,
            weak_concepts_json TEXT,
            summary_text TEXT,
            stats_json TEXT,
            cognitive_load_trend_json TEXT,
            recommendations_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
        )
        """)
