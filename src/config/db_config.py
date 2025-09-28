import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    @staticmethod
    def get_connection():
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL not set in environment variables")
        return psycopg2.connect(database_url)
