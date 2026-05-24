import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(encoding="utf-8-sig")


def _normalize_database_url(url: str) -> str:
    # Render/Heroku often provide postgres:// which psycopg2 expects as postgresql://
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rti_db")
)


def get_db_connection():
    """Returns a fresh connection to the PostgreSQL database."""
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise e


def init_db_schema() -> None:
    """Create application tables if they do not exist."""
    schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
    if not os.path.exists(schema_path):
        return

    with open(schema_path, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
        conn.commit()
    finally:
        conn.close()
