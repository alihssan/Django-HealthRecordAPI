"""
Script to set up the test database.
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_test_db():
    """Create test database if it doesn't exist."""
    # Get database connection parameters
    db_name = os.environ.get('POSTGRES_DB', 'healthrecords_test')
    db_user = os.environ.get('POSTGRES_USER', 'postgres')
    db_password = os.environ.get('POSTGRES_PASSWORD', 'postgres')
    db_host = os.environ.get('POSTGRES_HOST', 'localhost')
    db_port = os.environ.get('POSTGRES_PORT', '5432')

    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Check if database exists
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
    exists = cur.fetchone()
    
    if not exists:
        # Create database
        cur.execute(f'CREATE DATABASE {db_name}')
        print(f"Created test database: {db_name}")
    else:
        print(f"Test database {db_name} already exists")

    # Close connection
    cur.close()
    conn.close()

if __name__ == '__main__':
    setup_test_db() 