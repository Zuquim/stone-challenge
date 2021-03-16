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
    sp = SalesPerson(name="Dwight Kurt Schrute", email="schrute@dundermifflin.com")
    assert sp.table_name == "salesperson"
    assert sp.name == "Dwight Kurt Schrute"
    assert sp.email == "schrute.dwight@dundermifflin.com"
    assert sp.created is None
    assert sp.modified is None
    assert sp.exists_in_db(database_obj) is False
    with raises(expected_exception=NotImplementedError):
        sp.insert_into_db(database_obj)
        sp.update_data_in_db(database_obj)
        sp.soft_delete_data_in_db(database_obj)
        sp.export_dict()
        sp.import_dict({})
