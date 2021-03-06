from route_manager.db import (
    BaseModel,
    Database,
    build_key_value_template,
    datetime,
    fill_template_w_keys_n_values,
    log,
    sql,
)


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
        self.email = email  # UNIQUE

    def is_active(self, db_obj: Database) -> bool:
        if self.id <= -1:
            if not self.exists_in_db(db_obj):
                return False
        select = db_obj.select_rows(
            table=self.table_name,
            fields=["id", "name", "email", "created", "modified", "active"],
            filter=sql.SQL("WHERE {id} = {value}").format(
                id=sql.Identifier("id"), value=sql.Literal(self.id),
            ),
        )
        log.debug(f"SalesPerson.is_active(): select={select}")
        return select[0]["active"]

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
            table=self.table_name,
            fields=["id", "name", "email", "created", "modified", "active"],
            filter=filter,
        )
        log.debug(f"SalesPerson.exists_in_db(): select={select}")
        if len(select) == 1:
            self.set_id(int(select[0]["id"]))
            return True
        return False

    def insert_into_db(self, db_obj: Database) -> bool:
        self.created = datetime.now()
        return db_obj.insert_into(
            table=self.table_name,
            fields=("name", "email", "created"),
            values=(self.name, self.email, self.created),
        )

    def update_data_in_db(self, db_obj: Database) -> bool:
        if self.exists_in_db(db_obj) is False:
            log.error(f"Salesperson was not found in DB: {self}")
            return False
        self.modified = datetime.now()
        update_data = self._export_dict_for_query()
        return db_obj.update_rows_by_dict(
            table=self.table_name,
            field_value_dict=update_data,
            filter=sql.SQL("\nWHERE {id} = {self_id}").format(
                id=sql.Identifier("id"), self_id=sql.Literal(self.id)
            ),
        )

    def soft_delete_data_in_db(self, db_obj: Database) -> bool:
        self.active = False
        if self.update_data_in_db(db_obj):
            log.info(f"Salesperson was (soft) deleted from DB: {self}")
            return True
        return False

    def _export_dict_for_query(self) -> dict:
        return dict(
            name=self.name,
            email=self.email,
            modified=self.modified,
            active=self.active,
        )

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
            ),
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
