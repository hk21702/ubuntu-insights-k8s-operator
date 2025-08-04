# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Provides the DatabaseHandler class to handle database relation and state."""

import logging
from dataclasses import dataclass

from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
from ops import CharmBase, Object

DATABASE_NAME = "insights"

logger = logging.getLogger(__name__)


@dataclass
class DBData:
    """Data class for database relation data."""

    host: str = ""
    port: str = ""
    user: str = ""
    password: str = ""
    db_name: str = ""


class DatabaseHandler(Object):
    """The postgreSQL Database relation handler."""

    def __init__(self, charm: CharmBase, relation_name: str):
        """Initialize the handler and register event handlers.

        Args:
            charm: The charm instance.
            relation_name: The name of the database relation.
        """
        super().__init__(charm, "database-observer")
        self._charm = charm
        self.relation_name = relation_name
        self.database = DatabaseRequires(
            self._charm,
            relation_name=self.relation_name,
            database_name=DATABASE_NAME,
        )

    def get_relation_data(self) -> DBData:
        """Fetch the database relation data.

        If the relation is not ready or data is missing, an empty DBData instance is returned.

        Returns:
            A DBData instance containing the database relation data.
        """
        if self.model.get_relation(self.relation_name) is None or len(self.database.relations) < 1:
            logger.info("Could not find database relation: %s.", self.relation_name)
            return DBData()

        relation_id = self.database.relations[0].id
        try:
            relation_data = self.database.fetch_relation_data()[relation_id]
        except Exception as e:
            logger.warning("Error fetching relation data for %s: %s", self.relation_name, e)
            return DBData()

        endpoints = relation_data.get("endpoints", "").split(",")
        primary_endpoint = endpoints[0].split(":")
        if len(primary_endpoint) < 2:
            logger.info(
                "Could not parse primary endpoint from database relation data: %s", endpoints[0]
            )
            return DBData()

        logger.info("Fetched database endpoint: %s", primary_endpoint)

        if None in (
            relation_data.get("username"),
            relation_data.get("password"),
            relation_data.get("database"),
        ):
            return DBData()

        return DBData(
            host=primary_endpoint[0],
            port=primary_endpoint[1],
            user=relation_data["username"],
            password=relation_data["password"],
            db_name=relation_data["database"],
        )

    def is_relation_ready(self) -> bool:
        """Check if the database relation is ready.

        Returns:
            bool: True if the relation is ready, False otherwise.
        """
        return self.get_relation_data().host != ""
