from route_manager.db import BaseModel, Database, _connection, log, sql


class Client(BaseModel):
    """Client DB model."""

    def __init__(self, name: str):
        super().__init__(table_name="client")
        self.name = name


class Route(BaseModel):
    """Route DB model."""

    def __init__(self, name: str):
        super().__init__(table_name="route")
        self.name = name


class SalesPerson(BaseModel):
    """Salesperson DB model."""

    def __init__(self, name: str, email: str):
        super().__init__(table_name="salesperson")
        self.name = name
        self.email = email  # PK

    def exists_in_db(self, db_obj: Database) -> bool:
        if self.id >= 0:
            filter = sql.SQL("WHERE {id} = {value}").format(
                id=sql.Identifier("id"), value=sql.Literal(self.id),
            )
        else:
            filter = sql.SQL("WHERE {email} = {value}").format(
                email=sql.Identifier("email"), value=sql.Literal(self.email),
            )
        select = db_obj.select_rows(
            table=self.table_name, fields=["name", "email", "created"], filter=filter
        )
        log.debug(f"SalesPerson.exists_in_db(): select={select}")
        return len(select) >= 1

    def insert_into_db(self, db_obj: Database):
        raise NotImplementedError

    def update_data_in_db(self, db_obj: Database):
        raise NotImplementedError

    def soft_delete_data_in_db(self, db_obj: Database):
        raise NotImplementedError

    def export_dict(self) -> dict:
        return dict(
            table_name=self.table_name,
            row_data=dict(
                id=self.id,
                name=self.name,
                email=self.email,
                created=self.created,
                modified=self.modified,
                active=self.active,
            )
        )

    def __repr__(self) -> str:
        return (
            f"<SalesPerson("
            f"table_name='{self.table_name}'; "
            f"name='{self.name}'; "
            f"email='{self.email}'; "
            f"created={self.created}; "
            f"modified={self.modified}"
            f"ative={self.active}"
            f")>"
        )
