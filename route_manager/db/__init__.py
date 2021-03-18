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

    def create_tables(self):
        """Create needed DB tables."""
        self.connect()
        with self.conn.cursor() as cursor:
            with open("route_manager/sql/create_tables.sql") as q:
                cursor.execute(q.read())
            self.conn.commit()
            log.debug(f"Database.create_tables(): cursor.statusmessage='{cursor.statusmessage}'")

    def select_rows(
        self,
        table: str,
        fields: Union[str, list, tuple],
        filter: Union[str, sql.Composed] = "",
    ) -> List[DictRow]:
        """Run a SQL query to select rows from table."""
        query = sql.SQL("SELECT {fields} FROM {table} {filter}").format(
            fields=sql.Identifier(fields)
            if type(fields) is str
            else sql.SQL(", ").join(map(sql.Identifier, fields)),
            table=sql.Identifier(table),
            filter=sql.SQL(filter) if type(filter) is str else filter,
        )
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                log.info(f"{cursor.rowcount} rows selected")
                results = cursor.fetchall()
        except (Exception, DatabaseError) as e:
            log.error(e)
            return []
        else:
            return results
        finally:
            self.disconnect()

    def run_query_n_commit(
        self,
        query_tuple: Tuple[sql.Composed, Union[dict, tuple]],
    ) -> bool:
        """Run query (write into DB) and commit."""
        try:
            self.connect()
            with self.conn.cursor() as cursor:
                cursor.execute(*query_tuple)
                log.info(f"{cursor.rowcount} rows affected")
            self.conn.commit()
        except (Exception, DatabaseError) as e:
            log.error(f"Exception: {e}")
            return False
        else:
            return True
        finally:
            self.disconnect()

    def insert_into(
        self,
        table: str,
        fields: Union[list, tuple],
        values: Union[list, tuple],
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
        return self.run_query_n_commit((query, values))

    def insert_into_by_dict(self, table: str, field_value_dict: dict) -> bool:
        """Run a SQL query to insert data into a table."""
        query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
            table=sql.Identifier(table),
            fields=sql.SQL(", ").join(
                map(sql.Identifier, list(field_value_dict.keys()))
            ),
            values=sql.SQL(", ").join(map(sql.Placeholder, field_value_dict)),
        )
        return self.run_query_n_commit((query, field_value_dict))

    def update_rows_by_dict(
        self, table: str, field_value_dict: dict, filter: Union[str, sql.Composed]
    ) -> bool:
        """Run a SQL query to update rows in table."""
        query_prefix = sql.SQL("UPDATE {table} SET ").format(
            table=sql.Identifier(table)
        )
        query = fill_template_w_keys_n_values(
            query_prefix,
            field_value_dict,
            build_key_value_template(len(field_value_dict.keys())),
        )
        query += sql.SQL(filter) if type(filter) is str else filter
        return self.run_query_n_commit((query, None))


class BaseModel:
    """Base DB model."""

    def __init__(self, table_name: str):
        self.__id = -1  # PK
        self.table_name = table_name
        self.created = None
        self.modified = None
        self.active = True

    @property
    def id(self) -> int:
        return self.__id

    def set_id(self, id: int):
        if type(id) is not int or id <= -1:
            raise ValueError("Model ID must be an integer >= 0!")
        self.__id = id

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


def build_key_value_template(number_of_pairs: int) -> str:
    template = ""
    for _ in range(number_of_pairs):
        if "{key} = {value}" in template:
            template += ", \n"
        template += "{key} = {value}"
    return template


def fill_template_w_keys_n_values(
    query_prefix: sql.Composed, keys_values: dict, template: str
) -> sql.Composed:
    query = query_prefix
    for line, key, value in zip(
        template.splitlines(), keys_values.keys(), keys_values.values()
    ):
        query += sql.SQL(line).format(key=sql.Identifier(key), value=sql.Literal(value))
    return query
