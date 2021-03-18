from datetime import datetime

from pytest import raises

from route_manager.db import sql
from route_manager.db.models import Client, Route, SalesPerson


def test_client_init(database_obj):
    cli = Client(name="Phil Maguire")
    assert cli.table_name == "client"
    assert cli.id == -1
    assert cli.name == "Phil Maguire"
    assert cli.created is None
    assert cli.modified is None
    with raises(expected_exception=NotImplementedError):
        cli.exists_in_db(database_obj)
        cli.insert_into_db(database_obj)
        cli.update_data_in_db(database_obj)
        cli.soft_delete_data_in_db(database_obj)
        cli.export_dict()
        cli.import_dict({})


def test_route_init(database_obj):
    rt = Route(name="Golf Course")
    assert rt.table_name == "route"
    assert rt.id == -1
    assert rt.name == "Golf Course"
    assert rt.created is None
    assert rt.modified is None
    with raises(expected_exception=NotImplementedError):
        rt.exists_in_db(database_obj)
        rt.insert_into_db(database_obj)
        rt.update_data_in_db(database_obj)
        rt.soft_delete_data_in_db(database_obj)
        rt.export_dict()
        rt.import_dict({})


def test_salesperson_init(database_obj):
    table = "salesperson"
    name = "Dwight Kurt Schrute"
    email = "schrute@dundermifflin.com"

    sp = SalesPerson(name=name, email=email)
    assert sp.table_name == table
    assert sp.id == -1
    assert sp.name == name
    assert sp.email == email
    assert sp.created is None
    assert sp.modified is None
    assert sp.active is True
    assert sp.exists_in_db(database_obj) is False

    exported_data = sp.export_dict()
    assert type(exported_data) is dict
    assert type(exported_data["table_name"]) is str
    assert exported_data["table_name"] == table
    assert type(exported_data["row_data"]) is dict
    assert exported_data["row_data"]["name"] == name
    assert exported_data["row_data"]["email"] == email
    assert exported_data["row_data"]["created"] is None

    with raises(expected_exception=NotImplementedError):
        sp.import_dict({})


def test_client_crud(database_obj):
    table = "client"
    name = "Phil Maguire"

    cli = Client(name=name)
    assert cli.table_name == table
    assert cli.name == table


def test_route_crud(database_obj):
    table = "route"
    name = "Golf Course"

    rt = Route(name=name)
    assert rt.table_name == table
    assert rt.name == table


def test_salesperson_crud(database_obj):
    table = "salesperson"
    name = "Dwight Kurt Schrute"
    email = "schrute@dundermifflin.com"

    # Init
    sp = SalesPerson(name=name, email=email)
    assert sp.table_name == table
    assert sp.id == -1
    assert sp.name == name
    assert sp.email == email
    assert sp.created is None
    assert sp.exists_in_db(database_obj) is False

    # INSERT
    sp.insert_into_db(database_obj)
    assert sp.created <= datetime.now()
    assert sp.exists_in_db(database_obj) is True
    assert sp.id >= 0

    # UPDATE
    sp.name = "Dwight K. Schrute"
    sp.email = "schrute.dwight@dundermifflin.com"
    assert sp.exists_in_db(database_obj) is True
    rows = database_obj.select_rows(
        table=sp.table_name,
        fields=("id", "name", "email"),
        filter=sql.SQL("WHERE {field} = {email}").format(
            field=sql.Identifier("email"), email=sql.Literal(sp.email)
        ),
    )
    assert len(rows) == 0

    assert sp.update_data_in_db(database_obj) is True
    rows = database_obj.select_rows(
        table=sp.table_name,
        fields=("id", "name", "email"),
        filter=sql.SQL("WHERE {field} = {email}").format(
            field=sql.Identifier("email"), email=sql.Literal(sp.email)
        ),
    )
    assert len(rows) == 1
    assert sp.exists_in_db(database_obj) is True

    with raises(expected_exception=NotImplementedError):
        sp.soft_delete_data_in_db(database_obj)
