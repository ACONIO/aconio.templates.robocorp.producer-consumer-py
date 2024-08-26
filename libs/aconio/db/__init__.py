"""MSSQL database connection manager."""

from __future__ import annotations

import pymssql

from robocorp import vault


class Config:
    """Configuration for a database connection."""

    server: str = None
    database: str = None
    user: str = None
    password: str = None

    def __str__(self):
        pw_status = "UNSET"
        if self.password:
            pw_status = "SET"

        return (
            f"server={self.server}\n"
            + f"database={self.database}\n"
            + f"user={self.user}\n"
            + f"password={pw_status}\n"
        )


class MSSQLConnection:
    """MSSQL database connection manager."""

    def __init__(self) -> None:
        self._cfg = None
        self._conn = None

    def configure(self, cfg: Config) -> MSSQLConnection:
        """Configure MSSQL DB connection parameters.

        Args:
            cfg: Config object.
        """
        self._cfg = cfg
        return self

    def configure_from_vault(self, secret_name: str) -> MSSQLConnection:
        """Load DB config from Robocorp vault.

        The names of the properties of the secret must adhere to the following
        example:
        ```json
        {
            "server": "0.0.0.0",
            "database": "aconio",
            "user": "aconio",
            "password": "aconio"
        }
        ```

        Args:
            secret_name: Name of the vault secret.
        """

        cfg = Config()

        secret = vault.get_secret(secret_name)

        if "server" in secret:
            cfg.server = secret["server"]

        if "database" in secret:
            cfg.database = secret["database"]

        if "user" in secret:
            cfg.user = secret["user"]

        if "password" in secret:
            cfg.password = secret["password"]

        return self.configure(cfg)

    def connect(self) -> None:
        """Connect to the database.

        Raises:
            ValueError: If any of the required config values are missing.
            ConnectionError: If the connection attempt fails.
        """
        if self._cfg is None:
            raise ValueError(
                "Connection configuration unset. Did you call configure()?"
            )

        if self._cfg.server is None:
            raise ValueError("Config value 'server' is missing.")

        if self._cfg.database is None:
            raise ValueError("Config value 'database' is missing.")

        if self._cfg.user is None:
            raise ValueError("Config value 'user' is missing.")

        if self._cfg.password is None:
            raise ValueError("Config value 'password' is missing.")

        try:
            self._open_connection()
        except Exception as exc:
            raise ConnectionError(
                f"Failed to establish database connection: {exc}"
            ) from exc

    def is_connected(self) -> bool:
        return self._conn is not None

    def execute_query_from_file(self, sql_filepath: str, **kwargs) -> dict:
        """Read, parse, and execute sql statement from file.

        Args:
            sql_filepath:
                Path to the file containing the sql statement.

            **kwargs:
                Named Arguments passed to the `.format()` method of the
                sql statement string.

        Returns:
            Dictionary of the result of the query.

        Raises:
            RuntimeError: If the query execution fails.
        """
        # pylint: disable=unspecified-encoding
        with open(sql_filepath, "r") as file:
            sql_stmt = file.read().format(**kwargs)
            try:
                return self._execute_sql_stmt(sql_stmt)
            except Exception as exc:
                raise RuntimeError(f"Failed to execute query: {exc}") from exc

    def _open_connection(self):
        """Open connection to MSSQL Database."""
        self._conn = pymssql.connect(
            self._cfg.server,
            self._cfg.user,
            self._cfg.password,
            self._cfg.database,
        )

    def _execute_sql_stmt(self, sql_stmt: str) -> dict:
        """Open cursor, execute the sql statement, and return result."""
        with self._conn.cursor(as_dict=True) as cursor:
            cursor.execute(sql_stmt)

            return cursor.fetchall()
