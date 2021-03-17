from datetime import datetime

from psycopg2.extensions import STATUS_READY, STATUS_BEGIN
from pytest import raises

from route_manager.db import BaseModel


def test_manual_db_setup(setup_database):
    assert setup_database.status == STATUS_BEGIN

    cursor = setup_database.cursor()
    cursor.execute("SELECT * FROM test_users")
    assert cursor.rowcount == 2

def test_build_key_value_template():
    keys_values = dict(key1="value_A", key2="value_B", keyX="value_Y")
    template = build_key_value_template(len(keys_values.keys()))
    assert type(template) is str
    assert "{key} = {value}" in template
    assert len(template.splitlines()) == 3

def test_db_connection(database_connection):
    assert database_connection.status == STATUS_READY

def test_fill_template_w_keys_n_values():
    keys_values = dict(key1="value_A", key2="value_B", keyX="value_Y")
    template = build_key_value_template(len(keys_values.keys()))
    query_ = sql.SQL("UPDATE {table} SET ").format(table=sql.Identifier("table_name"))
    query = fill_template_w_keys_n_values(query_, keys_values, template)
    assert type(query) is sql.Composed

def test_db_init(database_obj):
    db = database_obj
    assert db.host == "db"
    assert db.port == 5432
    assert db.user == "manager"
    assert db.password == "R0ute-M4nager"
    assert db.dbname == "route_manager"
    assert db.conn is None


def test_base_model(database_obj):
    bm = BaseModel("base_table")
    assert bm.id == -1
    assert bm.table_name == "base_table"
    assert bm.created is None
    assert bm.modified is None
    assert bm.active is True
    with raises(expected_exception=NotImplementedError):
        bm.exists_in_db(database_obj)
        bm.insert_into_db(database_obj)
        bm.update_data_in_db(database_obj)
        bm.soft_delete_data_in_db(database_obj)
        bm.export_dict()
        bm.import_dict({})
