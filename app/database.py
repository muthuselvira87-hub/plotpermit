import psycopg

from app.config import get_settings


def get_db_connection():
    settings = get_settings()

    if not settings.database_url:
        raise ValueError("DATABASE_URL is missing from .env file")

    try:
        connection = psycopg.connect(settings.database_url)
        return connection

    except psycopg.Error as error:
        print(f"Database connection failed: {error}")
        raise