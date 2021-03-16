from datetime import datetime

from psycopg2.extensions import STATUS_READY, STATUS_BEGIN
from pytest import raises

from route_manager.db import BaseModel


def test_manual_db_setup(setup_database):
    assert setup_database.status == STATUS_BEGIN

    cursor = setup_database.cursor()
    cursor.execute("SELECT * FROM test_users")
    assert cursor.rowcount == 2


def test_db_connection(database_connection):
    assert database_connection.status == STATUS_READY


def test_db_init(database_obj):
    db = database_obj
    assert db.host == "db"
    assert db.port == 5432
    assert db.user == "manager"
    assert db.password == "R0ute-M4nager"
    assert db.dbname == "route_manager"
    assert db.conn is None


def test_base_model():
    bm = BaseModel("base_table")
    assert bm.id == -1
    assert bm.table_name == "base_table"
    assert bm.created <= datetime.now()
    assert bm.modified is None
    with raises(expected_exception=NotImplementedError):
        bm.export_dict()
        bm.import_dict({})
