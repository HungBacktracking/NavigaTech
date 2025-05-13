from typing import Optional
from uuid import uuid4, UUID
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)


