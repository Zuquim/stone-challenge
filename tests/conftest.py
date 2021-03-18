import pytest
# from pytest_postgresql.janitor import DatabaseJanitor

from route_manager.db import Database, _connection

_default_conn_params = dict(
    host="db",
    port=5432,
    user="manager",
    password="R0ute-M4nager",
    dbname="test_route_manager",
)



@pytest.fixture(scope="function")
def database_obj():
    """Using dummy database for testing purposes."""
    def drop_table(conn: _connection):
        """Making sure the DB is clean for testing."""
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS salesperson")
        conn.commit()

    # Connecting to DB
    db = Database(**_default_conn_params)
    db.connect()

    # Cleaning DB
    drop_table(db.conn)

    # Creating needed tables
    db.create_tables()

    # Yielding object for testing methods
    yield db

    # Cleaning DB
    drop_table(db.conn)

