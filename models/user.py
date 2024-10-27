from datetime import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, FileURI, file_uri
from models.auxillary.address import Address
from models.auxillary.phone_number import PhoneNumber
from models.opportunity import response

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))

    user_info: Mapped['User | None'] = relationship(back_populates='user_info')
    responses: Mapped[list[response.OpportunityResponse]] = \
        relationship(back_populates='user')

class UserInfo(Base):
    __tablename__ = 'user_info'

    user_id: Mapped[int] = \
        mapped_column(ForeignKey('user.id'), primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=True)
    surname: Mapped[str] = mapped_column(String(40), nullable=True)
    birthday: Mapped[datetime] = mapped_column(nullable=True)
    address_id: Mapped[int] = \
        mapped_column(ForeignKey('address.id'), nullable=True)
    # consider making unique
    phone_number_id: Mapped[int | None] = \
        mapped_column(ForeignKey('phone_number.id'), nullable=True)
    avatar: Mapped[file_uri] = mapped_column(FileURI, nullable=True)

    user: Mapped['User'] = relationship(back_populates='user')
    # consider adding backward relationship to address
    address: Mapped['Address | None'] = relationship()
    phone_number: Mapped['PhoneNumber | None'] = relationship()
    cvs: Mapped[list['CV']] = relationship(back_populates='cv')

    @property
    def fullname(self) -> str:
        return f'{self.name} {self.surname}'

class CV(Base):
    __tablename__ = 'cv'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_info_id: Mapped[int] = mapped_column(ForeignKey('user_info.user_id'))
    file: Mapped[file_uri] = mapped_column(FileURI)

    user_info: Mapped['UserInfo'] = relationship(back_populates='user_info')
