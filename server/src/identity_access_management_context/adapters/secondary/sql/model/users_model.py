from uuid import UUID
from typing import List
from sqlmodel import CheckConstraint, SQLModel, Field

class UserTable(SQLModel, table=True):
  __tablename__="UserTable"
  
  id: UUID = Field(default_factory=UUID, nullable=False, primary_key=True, index=True)
  username: str = Field(nullable=False)
  email: str = Field(nullable=False)
  name: str = Field(nullable=False)
  roles: List[str] = Field(default_factory=list)
