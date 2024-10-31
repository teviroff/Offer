from typing import Self
from datetime import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship

from utils import *
from models.base import Base, FileURI, file_uri
from models.auxillary.address import City
from models.auxillary.phone_number import PhoneNumber
import serializers.user as serializers

import logging

logger = logging.getLogger('database')

class CreateUserErrorCode(IntEnum):
    NON_UNIQUE_EMAIL = 0

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
    def create(cls, session: Session, fields: serializers.UserCredentials) \
            -> Self | GenericError[CreateUserErrorCode]:
        user = session.query(User).filter(User.email == fields.email).first()
        if user is not None:
            logger.debug('\'User.create\' exited with \'NON_UNIQUE_EMAIL\' '
                         'error (email=\'%s\')', fields.email)
            return GenericError(
                error_code=CreateUserErrorCode.NON_UNIQUE_EMAIL,
                error_message='User with given email already exists',
            )
        user = User(email=fields.email,
                    password_hash=cls.hash_password(fields.password))
        user.user_info = UserInfo(user=user)
        session.add(user)
        return user

class UpdateUserInfoErrorCode(IntEnum):
    INVALID_USER_ID = 0

class UserInfo(Base):
    __tablename__ = 'user_info'

    user_id: Mapped[int] = \
        mapped_column(ForeignKey('user.id'), primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=True)
    surname: Mapped[str] = mapped_column(String(40), nullable=True)
    birthday: Mapped[datetime] = mapped_column(nullable=True)
    city_id: Mapped[int] = \
        mapped_column(ForeignKey('city.id'), nullable=True)
    phone_number_id: Mapped[int | None] = \
        mapped_column(ForeignKey('phone_number.id'), unique=True, nullable=True)
    avatar: Mapped[file_uri] = mapped_column(FileURI, nullable=True)

    user: Mapped['User'] = relationship(back_populates='user_info')
    address: Mapped['City | None'] = relationship()
    phone_number: Mapped['PhoneNumber | None'] = relationship()
    cvs: Mapped[list['CV']] = \
        relationship(back_populates='user_info', cascade='all, delete-orphan')

    @property
    def fullname(self) -> str:
        return f'{self.name} {self.surname}'

    def __update_name(self, new_name: str, *args, **kwargs) -> None:
        self.name = new_name

    def __update_surname(self, new_surname: str, *args, **kwargs) -> None:
        self.surname = new_surname

    def __update_birthday(self, new_birthday: serializers.Date, *args, **kwargs) -> None:
        self.birthday = datetime(new_birthday.year, new_birthday.month,
                                 new_birthday.day)

    def __update_city(self, city_id: int, *args, **kwargs) -> None:
        self.city_id = city_id

    def __update_phone_number(
            self, new_phone_number: serializers.PhoneNumber, *args,
            session: Session, **kwargs
        ) -> None | GenericError[UpdateUserInfoErrorCode]:
        phone_number_or_error = \
            PhoneNumber.get_or_create(session, new_phone_number)
        if isinstance(phone_number_or_error, PhoneNumber):
            self.phone_number = phone_number_or_error
            return None
        return phone_number_or_error
    
    # TODO: add separate method for update
    def __update_avatar(self, new_avatar: file_uri, *args, **kwargs) -> None:
        self.avatar = new_avatar
    
    __field_handlers = (
        ('name', __update_name),
        ('surname', __update_surname),
        ('birthday', __update_birthday),
        ('city_id', __update_city),
        ('phone_number', __update_phone_number),
    )

    @classmethod
    def update(cls, session: Session, info: serializers.UserInfo) \
            -> None | GenericError[UpdateUserInfoErrorCode]:
        user: User | None = session.query(User).get(info.user_id)
        if user is None:
            logger.debug('\'UserInfo.update\' exited with \'INVALID_USER_ID\' '
                         'error (user_id=%i)', info.user_id)
            return GenericError(
                error_code=UpdateUserInfoErrorCode.INVALID_USER_ID,
                error_message='User with provided id doesn\'t exist'
            )
        for field, handler in UserInfo.__field_handlers:
            if getattr(info, field) is None:
                continue
            error_or_none = \
                handler(user.user_info, getattr(info, field), session=session)
            if error_or_none is not None:
                return error_or_none

    @classmethod
    def update_avatar(cls, session: Session, ) -> None:
        ... # TODO

class CV(Base):
    __tablename__ = 'cv'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_info_id: Mapped[int] = mapped_column(ForeignKey('user_info.user_id'))
    file: Mapped[file_uri] = mapped_column(FileURI)

    user_info: Mapped['UserInfo'] = relationship(back_populates='cvs')

# magic fix, placing it in the beggining of a file results in error on line 19
from models.opportunity import response
