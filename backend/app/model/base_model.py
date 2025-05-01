from uuid import uuid4, UUID
from sqlalchemy import Field, SQLModel


class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)


