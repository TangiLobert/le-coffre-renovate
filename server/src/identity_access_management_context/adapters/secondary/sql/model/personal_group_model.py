from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4


class PersonalGroupTable(SQLModel, table=True):
    __tablename__: str = "PersonalGroupTable"

    id: UUID = Field(
        default_factory=uuid4, nullable=False, primary_key=True, index=True
    )
    name: str = Field(nullable=False)
    user_id: UUID = Field(nullable=False, index=True)


def create_personal_group_table(engine):
    SQLModel.metadata.create_all(engine)
