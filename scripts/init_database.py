"""
Database initialization script for AEGIS-X.

Creates all PostgreSQL tables defined in backend/models/database.py.
Run this once before starting the application for the first time.

Usage:
    python -m scripts.init_database

Requirements:
    - PostgreSQL server running on configured host/port
    - Database 'aegisx' created (CREATE DATABASE aegisx;)
    - Valid credentials in .env file
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.database import Base, engine, init_db


def main():
    print("[AEGIS-X] Initializing database schema...")
    print(f"[AEGIS-X] Engine: {engine.url}")

    try:
        init_db()
        print("[AEGIS-X] All tables created successfully.")

        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"[AEGIS-X] Tables: {', '.join(tables)}")

    except Exception as e:
        print(f"[AEGIS-X] Database initialization failed: {e}")
        print("[AEGIS-X] Ensure PostgreSQL is running and .env is configured correctly.")
        sys.exit(1)


if __name__ == "__main__":
    main()
