# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import contextlib
from unittest.mock import MagicMock, PropertyMock, patch

from ops.model import ModelError

from database import DatabaseHandler, DBData


def test_dbdata_defaults():
    """Test that DBData defaults to empty strings."""
    db = DBData()
    assert db.host == ""
    assert db.port == ""
    assert db.user == ""
    assert db.password == ""
    assert db.db_name == ""


def test_get_relation_data_no_relation():
    """Test that get_relation_data returns empty DBData when no relation exists."""
    charm = MagicMock()
    handler = DatabaseHandler(charm, "database")
    handler.model.get_relation = MagicMock(return_value=None)
    assert handler.get_relation_data() == DBData()


@contextlib.contextmanager
def handler_with_mocked_relation(relation_data, relation_id=1):
    charm = MagicMock()
    handler = DatabaseHandler(charm, "database")
    handler.model.get_relation = MagicMock(return_value=True)
    with patch.object(
        type(handler.database), "relations", new_callable=PropertyMock
    ) as mock_relations:
        mock_relations.return_value = [MagicMock(id=relation_id)]
        handler.database.fetch_relation_data = MagicMock(return_value=relation_data)
        yield handler


def test_get_relation_data_no_endpoints():
    """Test that get_relation_data returns empty DBData when no endpoints are found."""
    with handler_with_mocked_relation({0: {}, 1: {"endpoints": ""}}, relation_id=0) as handler:
        assert handler.get_relation_data() == DBData()

    with handler_with_mocked_relation({1: {"endpoints": ""}}, relation_id=1) as handler:
        assert handler.get_relation_data() == DBData()


def test_get_relation_data_fetch_exception():
    """Test empty return when fetch_relation_data raises exception."""
    with handler_with_mocked_relation({}, relation_id=1) as handler:
        handler.database.fetch_relation_data = MagicMock(
            side_effect=ModelError("permission denied")
        )
        assert handler.get_relation_data() == DBData()


def test_get_relation_data_malformed_endpoint():
    """Test that get_relation_data returns empty DBData when endpoints are malformed."""
    with handler_with_mocked_relation({1: {"endpoints": "badendpoint"}}, relation_id=1) as handler:
        assert handler.get_relation_data() == DBData()


def test_get_relation_data_missing_fields():
    with handler_with_mocked_relation(
        {
            1: {
                "endpoints": "host:1234",
                "username": None,
                "password": None,
                "database": None,
            }
        },
        relation_id=1,
    ) as handler:
        assert handler.get_relation_data() == DBData()


def test_get_relation_data_valid():
    """Test that get_relation_data returns valid DBData when all fields are present and valid."""
    with handler_with_mocked_relation(
        {
            1: {
                "endpoints": "host:1234",
                "username": "user",
                "password": "pass",
                "database": "db",
            }
        },
        relation_id=1,
    ) as handler:
        db = handler.get_relation_data()
        assert db.host == "host"
        assert db.port == "1234"
        assert db.user == "user"
        assert db.password == "pass"
        assert db.db_name == "db"


def test_is_relation_ready_true():
    """Test that is_relation_ready returns True when relation data is valid."""
    charm = MagicMock()
    handler = DatabaseHandler(charm, "database")
    handler.get_relation_data = MagicMock(return_value=DBData(host="host"))
    assert handler.is_relation_ready() is True


def test_is_relation_ready_false():
    """Test that is_relation_ready returns False when relation data is not valid."""
    charm = MagicMock()
    handler = DatabaseHandler(charm, "database")
    handler.get_relation_data = MagicMock(return_value=DBData(host=""))
    assert handler.is_relation_ready() is False
