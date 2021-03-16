from route_manager.db import BaseModel


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
        self.email = email

    def __repr__(self) -> str:
        return (
            f"<SalesPerson("
            f"table_name='{self.table_name}'; "
            f"name='{self.name}'; "
            f"email='{self.email}'; "
            f"created={self.created}; "
            f"modified={self.modified}"
            f")>"
        )
