import os
import sqlite3

from collections.abc import Iterator
from pathlib import Path

from ra_platform.persistence.sqlite import (
    create_connection,
    initialize_database,
)


def get_database_path() -> Path:
    return Path(
        os.getenv(
            "RA_DB_PATH",
            "data/paradigm_ra.db",
        )
    )


def get_database_connection() -> Iterator[
    sqlite3.Connection
]:
    connection = create_connection(
        get_database_path()
    )

    initialize_database(connection)

    try:
        yield connection
    finally:
        connection.close()