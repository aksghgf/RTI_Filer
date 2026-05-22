# core/db.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv(encoding="utf-8-sig")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rti_db")

def get_db_connection():
    """Returns a fresh connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Database Connection Error: {str(e)}")
        raise e