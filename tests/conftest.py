import psycopg2
import pytest
from psycopg2.extras import DictCursor

from route_manager.db import Database

_conn_params = dict(
    host='db',
    port=5432,
    user='manager',
    password='R0ute-M4nager',
    dbname='route_manager',
)


@pytest.fixture
def database_connection():
    db = Database(**_conn_params)
    db.connect()
    yield db.conn
    db.conn.rollback()
    db.disconnect()


@pytest.fixture
def database_obj():
    yield Database(**_conn_params)


@pytest.fixture
def setup_database():
    conn = psycopg2.connect(**_conn_params)
    cursor = conn.cursor(cursor_factory=DictCursor)

    cursor.execute("DROP TABLE IF EXISTS test_users")

    sql_create_table = """ 
        CREATE TABLE test_users (
            user_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL, 
            created TIMESTAMP NOT NULL, 
            modified TIMESTAMP
        )
    """
    cursor.execute(sql_create_table)

    sql_insert = "INSERT INTO test_users (name, created, modified) VALUES (%s, %s, %s)"
    sample_data = [
        ("Jim Halpert", "2005-01-01 00:00:00", "2014-01-01 20:00:00"),
        ("Pam Beesly", "2005-01-01 01:00:00", "2014-01-01 08:00:00"),
    ]
    cursor.executemany(sql_insert, sample_data)
    cursor.execute("SELECT * FROM test_users")
    yield conn
    conn.rollback()
    conn.close()
