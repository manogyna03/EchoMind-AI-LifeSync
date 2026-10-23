import os
import sqlite3
from typing import Generator
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "echomind.db")


def get_db_connection():
    """Create a connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_session() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for safe database transactions."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database tables for LifeSync Intelligence."""
    with db_session() as conn:
        cursor = conn.cursor()

        # 1. Tasks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT DEFAULT 'general',
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                due_date TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)

        # 2. Schedule Events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule_events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                event_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                duration_mins INTEGER DEFAULT 30,
                location TEXT DEFAULT '',
                category TEXT DEFAULT 'general',
                is_completed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # 3. Memory Items (LifeSync Long-Term Memory)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_items (
                id TEXT PRIMARY KEY,
                key_topic TEXT NOT NULL,
                value_fact TEXT NOT NULL,
                category TEXT DEFAULT 'personal',
                confidence REAL DEFAULT 1.0,
                updated_at TEXT NOT NULL
            )
        """)

        # 4. Reminders
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                due_time TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                is_active INTEGER DEFAULT 1,
                category TEXT DEFAULT 'general',
                created_at TEXT NOT NULL
            )
        """)

        # 5. Purchases (Alexa+ simulated orders and approvals)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id TEXT PRIMARY KEY,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                estimated_price REAL DEFAULT 0.0,
                status TEXT DEFAULT 'pending_approval',
                store TEXT DEFAULT 'Amazon',
                created_at TEXT NOT NULL
            )
        """)

        # 6. Smart Home Devices (Simulated IoT Devices)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS smart_devices (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                room TEXT NOT NULL,
                device_type TEXT NOT NULL,
                state_json TEXT NOT NULL,
                is_simulated INTEGER DEFAULT 1,
                disclaimer TEXT DEFAULT 'Simulated device for Amazon Alexa+ testing without hardware requirement.'
            )
        """)
