from datetime import datetime

from pytest import raises

from route_manager.db.models import Client, Route, SalesPerson


def test_client_init(database_obj):
    cli = Client(name="Phil Maguire")
    assert cli.table_name == "client"
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
