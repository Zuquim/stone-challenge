from datetime import datetime

from pytest import raises

from route_manager.db.models import Client, Route, SalesPerson


def test_client_init():
    cli = Client(name="Phil Maguire")
    assert cli.table_name == "client"
    assert cli.name == "Phil Maguire"
    assert cli.created <= datetime.now()
    assert cli.modified is None
    with raises(expected_exception=NotImplementedError):
        cli.export_dict()
        cli.import_dict({})


def test_route_init():
    route = Route(name="Golf Course")
    assert route.table_name == "route"
    assert route.name == "Golf Course"
    assert route.created <= datetime.now()
    assert route.modified is None
    with raises(expected_exception=NotImplementedError):
        route.export_dict()
        route.import_dict({})


def test_salesperson_init():
    sp = SalesPerson(name="Dwight Kurt Schrute", email="schrute.dwight@dundermifflin.com")
    assert sp.table_name == "salesperson"
    assert sp.name == "Dwight Kurt Schrute"
    assert sp.email == "schrute.dwight@dundermifflin.com"
    assert sp.created <= datetime.now()
    assert sp.modified is None
    with raises(expected_exception=NotImplementedError):
        sp.export_dict()
        sp.import_dict({})
