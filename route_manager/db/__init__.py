from datetime import datetime
from logging import DEBUG, INFO
from typing import Any, List, Optional, Tuple, Union

from logzero import setup_logger
from psycopg2 import DatabaseError, connect, sql
from psycopg2.extras import DictCursor, DictRow, _connection

log = setup_logger(
    name="db",
    level=INFO,
    logfile="logs/app.log",
    fileLoglevel=DEBUG,
    maxBytes=512000,
    backupCount=2,
)


class Database:
    """PostgreSQL Database class."""

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        dbname: str,
        port: Union[int, str] = 5432,
    ):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__dbname = dbname
        self.__connection = None

    @property
    def host(self) -> str:
        """Return database host."""
        return self.__host

    @property
    def port(self) -> str:
        """Return database port."""
        return self.__port

    @property
    def user(self) -> str:
        """Return database username."""
        return self.__user

    @property
    def password(self) -> str:
        """Return database password."""
        return self.__password

    @property
    def dbname(self) -> str:
        """Return database name."""
        return self.__dbname

    @property
    def conn(self) -> Optional[_connection]:
        """Return database connection object if it exists, else None."""
        return self.__connection

    def connect(self) -> None:
        """Connect to a Postgres database."""
        if self.conn is None:
            try:
                self.__connection = connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port,
                    dbname=self.dbname,
                    cursor_factory=DictCursor,
                )
            except DatabaseError as e:
                log.exception(e)
            else:
                log.info("Connection opened successfully")
        else:
            log.info("Connection was already open")

    def disconnect(self) -> None:
        """Disconnects from Postgres database."""
        if self.conn is _connection:
            try:
                self.conn.close()
            except DatabaseError as e:
                log.exception(e)
            else:
                self.__connection = None
                log.info("Connection closed successfully")
        else:
            log.info("Connection was already closed")

    def select_rows(
        self,
        table: str,
        fields: Union[str, List[str], Tuple[str]],
        filter: Union[str, sql.Composed] = "",
    ) -> List[DictRow]:
        """Run a SQL query to select rows from table."""
        query = sql.SQL("SELECT {fields} FROM {table} {filter}").format(
            fields=sql.Identifier(fields)
            if type(fields) is str
            else sql.SQL(", ").join(map(sql.Identifier, fields)),
            table=sql.Identifier(table),
            filter=filter if type(filter) is sql.Composed else sql.SQL(filter),
        )
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                log.info(f"{cursor.rowcount} rows selected")
        except (Exception, DatabaseError) as e:
            log.error(e)
            return []
        else:
            return cursor.fetchall()

    def insert_into(
        self,
        table: str,
        fields: Union[List[str], Tuple[str]],
        values: Union[List[Any], Tuple[Any]],
    ) -> bool:
        """Run a SQL query to insert data into a table."""
        if len(fields) != len(values):
            raise ValueError(
                f"'fields'({len(fields)}) and 'values'({len(values)}) must have the same amount of items!"
            )
        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
            table=sql.Identifier(table),
            fields=sql.SQL(", ").join(map(sql.Identifier, fields)),
            values=sql.SQL(", ").join(sql.Placeholder() * len(values)),
        )
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                cursor.execute(query, values)
                self.conn.commit()
                log.info(f"{cursor.rowcount} rows affected")
        except (Exception, DatabaseError) as e:
            log.error(e)
            return False
        else:
            return True

    def insert_into_by_dict(self, table: str, field_value_dict: dict) -> bool:
        """Run a SQL query to insert data into a table."""
        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
            table=sql.Identifier(table),
            fields=sql.SQL(", ").join(
                map(sql.Identifier, list(field_value_dict.keys()))
            ),
            values=sql.SQL(", ").join(map(sql.Placeholder, field_value_dict)),
        )
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                cursor.execute(query, field_value_dict)
                self.conn.commit()
                log.info(f"{cursor.rowcount} rows affected")
        except (Exception, DatabaseError) as e:
            log.error(e)
            return False
        else:
            return True

    def update_rows(self, query) -> str:
        """Run a SQL query to update rows in table."""
        raise NotImplementedError


class BaseModel:
    """Base DB model."""

    def __init__(self, table_name: str):
        self.id = -1  # DB PK
        self.table_name = table_name
        self.created = None
        self.modified = None

    def exists_in_db(self, db_obj: Database) -> bool:
        """Checks if this object already exists inside DB."""
        raise NotImplementedError

    def insert_into_db(self, db_obj: Database) -> bool:
        """Inserts object data into DB."""
        raise NotImplementedError

    def update_data_in_db(self, db_obj: Database) -> bool:
        """Updates related row in DB according to this object's data."""
        raise NotImplementedError

    def soft_delete_data_in_db(self, db_obj: Database) -> bool:
        """Soft deletes related row in DB (set to inactive/disabled)."""
        raise NotImplementedError

    def export_dict(self) -> dict:
        """Exports DB model as dictionary."""
        raise NotImplementedError

    def import_dict(self, data_dict: dict) -> None:
        """Imports DB data as dictionary."""
        raise NotImplementedError

    def __str__(self) -> str:
        return self.__repr__()