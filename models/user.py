from typing import Self, Union
from datetime import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship

from utils import *
from models.base import Base, FileURI, file_uri
from models.auxillary.address import City
# from models.auxillary.phone_number import PhoneNumber
import serializers.mod as ser

import logging

logger = logging.getLogger('database')


class CreateUserErrorCode(IntEnum):
    NON_UNIQUE_EMAIL = 0

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))

    user_info: Mapped['UserInfo'] = relationship(back_populates='user', cascade='all, delete-orphan')
    responses: Mapped[list['response.OpportunityResponse']] = \
        relationship(back_populates='user', cascade='all, delete-orphan')

    @classmethod
    def hash_password(cls, password: str) -> str:
        from hashlib import sha256

        return sha256(password.encode()).hexdigest()

    @classmethod
    def create(cls, session: Session, request: ser.User.Create) -> Self | GenericError[CreateUserErrorCode]:
        user = session.query(User).filter(User.email == request.email).first()
        if user is not None:
            logger.debug('\'User.create\' exited with \'NON_UNIQUE_EMAIL\' error (email=\'%s\')', request.email)
            return GenericError(error_code=CreateUserErrorCode.NON_UNIQUE_EMAIL,
                                error_message='User with given email already exists')
        user = User(email=request.email, password_hash=cls.hash_password(request.password))
        user.user_info = UserInfo(user=user)
        session.add(user)
        return user

    @classmethod
    def login(cls, session: Session, request: ser.User.Login) -> Self | None:
        user: User | None = session.query(User).filter(User.email == request.email).first()
        if user is None:
            logger.debug('\'User.login\' exited because user with given email doesn\'t exist '
                         '(email=\'%s\')', request.email)
            return None
        if user.password_hash != cls.hash_password(request.password):
            logger.debug('\'User.login\' exited because user with given email have different password '
                         '(email=\'%s\')', request.email)
            return None
        return user

    # TODO
    @classmethod
    def change_password(cls, session: Session, request: ...) -> None:
        ...

    @classmethod
    def get_info(cls, session: Session, user_id: int) -> dict | None:
        user: User | None = session.query(User).get(user_id)
        if user is None:
            return
        return {
            'name': user.user_info.name,
            'surname': user.user_info.surname,
            'birthday': user.user_info.birthday.strftime('%Y-%m-%d') if user.user_info.birthday is not None else None,
            # TODO: city, phone number, avatar
        }


class UpdateUserInfoErrorCode(IntEnum):
    INVALID_USER_ID = 0

class UserInfo(Base):
    __tablename__ = 'user_info'

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=True)
    surname: Mapped[str] = mapped_column(String(40), nullable=True)
    birthday: Mapped[datetime] = mapped_column(nullable=True)
    city_id: Mapped[int] = mapped_column(ForeignKey('city.id'), nullable=True)
    phone_number_id: Mapped[int | None] = mapped_column(ForeignKey('phone_number.id'), unique=True, nullable=True)
    avatar: Mapped[file_uri] = mapped_column(FileURI, nullable=True)

    user: Mapped['User'] = relationship(back_populates='user_info')
    address: Mapped[Union['City', None]] = relationship()
    phone_number: Mapped['PhoneNumber | None'] = relationship()
    cvs: Mapped[list['CV']] = relationship(back_populates='user_info', cascade='all, delete-orphan')

    @property
    def fullname(self) -> str:
        return f'{self.name} {self.surname}'

    def __update_name(self, new_name: str, *args, **kwargs) -> None:
        self.name = new_name

    def __update_surname(self, new_surname: str, *args, **kwargs) -> None:
        self.surname = new_surname

    def __update_birthday(self, new_birthday: ser.auxillary.Date, *args, **kwargs) -> None:
        self.birthday = datetime(new_birthday.year, new_birthday.month, new_birthday.day)

    def __update_city(self, city_id: int, *args, **kwargs) -> None:
        self.city_id = city_id

    __update_field_handlers = (
        ('name', __update_name),
        ('surname', __update_surname),
        ('birthday', __update_birthday),
        ('city_id', __update_city),
    )

    @classmethod
    def update(cls, session: Session, request: ser.UserInfo.Update) -> None | GenericError[UpdateUserInfoErrorCode]:
        user: User | None = session.query(User).get(request.user_id)
        if user is None:
            logger.debug('\'UserInfo.update\' exited with \'INVALID_USER_ID\' error (user_id=%i)', request.user_id)
            return GenericError(
                error_code=UpdateUserInfoErrorCode.INVALID_USER_ID,
                error_message='User with provided id doesn\'t exist'
            )
        for field, handler in UserInfo.__update_field_handlers:
            if getattr(request, field) is None:
                continue
            error_or_none = handler(user.user_info, getattr(request, field), session=session)
            if error_or_none is not None:
                return error_or_none

    # TODO
    @classmethod
    def update_phone_number(cls, session: Session, request: ...) -> None:
        ...

    # TODO
    @classmethod
    def update_avatar(cls, session: Session, request: ser.UserInfo.UpdateAvatar) -> None:
        ...


class DeleteCVErrorCode(IntEnum):
    INVALID_CV_ID = 0

class CV(Base):
    __tablename__ = 'cv'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_info_id: Mapped[int] = mapped_column(ForeignKey('user_info.user_id'))
    file: Mapped[file_uri] = mapped_column(FileURI)

    user_info: Mapped['UserInfo'] = relationship(back_populates='cvs')

    # TODO
    @classmethod
    def create(cls, session: Session, request: ser.CV.Create) -> None:
        ...

    @classmethod
    def delete(cls, session: Session, request: ser.CV.Delete) -> None | GenericError[DeleteCVErrorCode]:
        cv: CV | None = session.query(CV).get(request.cv_id)
        if cv is None:
            logger.debug('\'CV.delete\' exited with \'INVALID_CV_ID\' error (cv_id=%i)', request.cv_id)
            return GenericError(
                error_code=DeleteCVErrorCode.INVALID_CV_ID,
                error_message='CV with provided id doesn\'t exist'
            )
        session.delete(cv)
        return None


# magic fix, placing it in the beggining of a file results in error
from models.opportunity import response
