from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

class Country(Base):
    __tablename__ = 'country'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    phone_code: Mapped[str] = mapped_column(String(3))

    cities: Mapped[list['City']] = relationship(back_populates='country')

class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id'))
    name: Mapped[str] = mapped_column(String(50))

    country: Mapped['Country'] = relationship(back_populates='cities')
    streets: Mapped[list['Street']] = relationship(back_populates='city')

class Street(Base):
    __tablename__ = 'street'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(ForeignKey('city.id'))
    name: Mapped[str] = mapped_column(String(50))

    city: Mapped['City'] = relationship(back_populates='streets')
    addresses: Mapped[list['Address']] = relationship(back_populates='street')

class Address(Base):
    __tablename__ = 'address'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    street_id: Mapped[int] = mapped_column(ForeignKey('street.id'))
    house: Mapped[int]

    street: Mapped['Street'] = relationship(back_populates='addresses')
