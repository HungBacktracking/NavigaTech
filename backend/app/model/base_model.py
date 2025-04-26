from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    id: int = Field(primary_key=True)
