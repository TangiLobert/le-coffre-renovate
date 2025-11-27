from typing import Optional
from uuid import UUID
from model import UserTable
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from identity_access_management_context.application.gateways import UserRepository
from identity_access_management_context.domain.entities import User
from identity_access_management_context.domain.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
)
from shared_kernel.authentication.constants import ADMIN_ROLE

class SqlUserRepository(UserRepository):
  def __init__(self, Session):
    self._session = Session
  
  def get_by_id(self, user_id: UUID) -> Optional[User]:
    statement = select(UserTable).where(UserTable.id == user_id)
    result = self._session.exec(statement).first()
    if result is None:
      raise UserNotFoundError(id)
    return result
  
  def get_by_email(self, email: str) -> Optional[User]:
    statement = select(UserTable).where(UserTable.email == email)
    result = self._session.exec(statement).all()
    if not result:
      raise UserNotFoundError(email)
    return result
  
  def list_all(self) -> list[User]:
    statement = select(UserTable)
    results = self._session.exec(statement).all()
    return results

  def save(self, user: User) -> None:
    db_obj = UserTable.model_validate(user)
    self._session.add(db_obj)
    try:
      self._session.commit()
      self._session.refresh(db_obj)
    except IntegrityError:
      self._session.rollback()
      raise UserAlreadyExistsError(user.username)
  
  def delete(self, user: User) -> None:
    statement = select(UserTable).where(UserTable.id == user.id)
    db_obj = self._session.exec(statement).first()
    if db_obj is None:
      raise UserNotFoundError(user.id)
    self._session.delete(db_obj)
    self._session.commit()

  def update(self, user : User) -> None:
    statement = select(UserTable).where(UserTable.id == user.id)
    db_obj = self._session.exec(statement).first()
    if db_obj is None:
      raise UserNotFoundError(user.id)
    for key, value in vars(user).items():
      setattr(db_obj, key, value)
    self._session.add(db_obj)
    self._session.commit()
    self._session.refresh(db_obj)
    
  def get_admin(self) -> Optional[User]:
    statement = select(UserTable).where(UserTable.roles.contains([ADMIN_ROLE]))
    result = self._session.exec(statement).first()
    if result is None:
      raise UserNotFoundError(ADMIN_ROLE)
    return result
