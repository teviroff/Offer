from typing import Self
from datetime import datetime
from enum import IntEnum
from dataclasses import dataclass

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import (
    Session, Mapped, mapped_column, relationship, object_session
)

from models.base import Base, FileURI, file_uri
from models.auxillary.address import Address
from models.auxillary.phone_number import PhoneNumber
import models.dataclasses as _

import logging

logger = logging.getLogger('database')

class CreateUserErrorCode(IntEnum):
    NON_UNIQUE_EMAIL = 0

@dataclass
class CreateUserError:
    error_code: CreateUserErrorCode
    error_message: str

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))

    user_info: Mapped['UserInfo | None'] = \
        relationship(back_populates='user', cascade='all, delete-orphan')
    responses: Mapped[list['response.OpportunityResponse']] = \
        relationship(back_populates='user', cascade='all, delete-orphan')

    @classmethod
    def hash_password(cls, password: str) -> str:
        from hashlib import sha256

        return sha256(password.encode()).hexdigest()

    @classmethod
    def create(cls, session: Session, credentials: _.UserCredentials) -> Self | CreateUserError:
        user = session.query(User).filter(User.email == credentials.email).first()
        if user is not None:
            logger.debug('\'User.create\' exited with \'NON_UNIQUE_EMAIL\' '
                         'error (email=\'%s\')', credentials.email)
            return CreateUserError(
                error_code=CreateUserErrorCode.NON_UNIQUE_EMAIL,
                error_message='User with given email already exists',
            )
        user = User(email=credentials.email,
                    password_hash=cls.hash_password(credentials.password))
        user.user_info = UserInfo(user=user)
        session.add(user)
        return user

class UpdateUserInfoErrorCode(IntEnum):
    NO_ACTIVE_SESSION = 0

@dataclass
class UpdateUserInfoError:
    error_code: UpdateUserInfoErrorCode
    error_message: str

class UserInfo(Base):
    __tablename__ = 'user_info'

    user_id: Mapped[int] = \
        mapped_column(ForeignKey('user.id'), primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=True)
    surname: Mapped[str] = mapped_column(String(40), nullable=True)
    birthday: Mapped[datetime] = mapped_column(nullable=True)
    address_id: Mapped[int] = \
        mapped_column(ForeignKey('address.id'), nullable=True)
    phone_number_id: Mapped[int | None] = \
        mapped_column(ForeignKey('phone_number.id'), unique=True, nullable=True)
    avatar: Mapped[file_uri] = mapped_column(FileURI, nullable=True)

    user: Mapped['User'] = relationship(back_populates='user_info')
    address: Mapped['Address | None'] = relationship()
    phone_number: Mapped['PhoneNumber | None'] = relationship()
    cvs: Mapped[list['CV']] = \
        relationship(back_populates='user_info', cascade='all, delete-orphan')

    @property
    def fullname(self) -> str:
        return f'{self.name} {self.surname}'

    def __update_name(self, new_name: str) -> None:
        self.name = new_name

    def __update_surname(self, new_surname: str) -> None:
        self.surname = new_surname

    def __update_birthday(self, new_birthday: _.Date) -> None:
        self.birthday = datetime(new_birthday.year, new_birthday.month,
                                 new_birthday.day)

    def __get_session(self) -> Session | UpdateUserInfoError:
        session = object_session(self)
        if session is None:
            logger.debug('\'UserInfo.update\' exited with \'NO_ACTIVE_SESSION\' '
                         'error (id=%i)', self.user_id)
            return UpdateUserInfoError(
                error_code=UpdateUserInfoErrorCode.NO_ACTIVE_SESSION,
                error_message='No active session found for this \'UserInfo\'',
            )
        return session

    def __update_address(self, new_address: _.Address) -> None | UpdateUserInfoError:
        session = self.__get_session()
        if not isinstance(session, Session):
            return session
        self.address = Address.get_or_create(session, new_address)

    def __update_phone_number(self, new_phone_number: _.PhoneNumber) -> None | UpdateUserInfoError:
        session = self.__get_session()
        if not isinstance(session, Session):
            return session
        self.phone_number = PhoneNumber.get_or_create(session, new_phone_number)
    
    def __update_avatar(self, new_avatar: file_uri) -> None:
        self.avatar = new_avatar
    
    __field_handlers = (
        ('name', __update_name),
        ('surname', __update_surname),
        ('birthday', __update_birthday),
        ('address', __update_address),
        ('phone_number', __update_phone_number),
        ('avatar', __update_avatar),
    )

    def update(self, new_fields: _.UserInfo) -> None | UpdateUserInfoError:
        for field, handler in UserInfo.__field_handlers:
            if getattr(new_fields, field) is None:
                continue
            result = handler(self, getattr(new_fields, field))
            if result is not None:
                return result

class CV(Base):
    __tablename__ = 'cv'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_info_id: Mapped[int] = mapped_column(ForeignKey('user_info.user_id'))
    file: Mapped[file_uri] = mapped_column(FileURI)

    user_info: Mapped['UserInfo'] = relationship(back_populates='cvs')

# magic fix, placing it in the beggining of a file results in error on line 19
from models.opportunity import response