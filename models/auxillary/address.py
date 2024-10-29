from typing import Self

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship

from models.base import Base
import models.dataclasses as _

import logging

logger = logging.getLogger('database')

class Country(Base):
    __tablename__ = 'country'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    phone_code: Mapped[str] = mapped_column(String(3), nullable=True)

    cities: Mapped[list['City']] = relationship(back_populates='country')

    @classmethod
    def get_or_create(cls, session: Session, name: str) -> Self:
        country = session.query(Country).filter(Country.name == name).first()
        if country is None:
            logger.debug('Creating new \'Country\' instance (name=\'%s\')', name)
            country = Country(name=name)
            session.add(country)
        return country

class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id'))
    name: Mapped[str] = mapped_column(String(50))

    country: Mapped['Country'] = relationship(back_populates='cities')
    streets: Mapped[list['Street']] = relationship(back_populates='city')

    @classmethod
    def get_or_create(cls, session: Session, city_name: str,
                      country_name: str) -> Self:
        country = Country.get_or_create(session, country_name)
        city = session.query(City) \
            .filter(City.name == city_name, City.country == country).first()
        if city is None:
            logger.debug('Creating new \'City\' instance (name=\'%s\', '
                         'country=\'%s\')', city_name, country.name)
            city = City(name=city_name, country=country)
            session.add(city)
        return city

    @property
    def full(self) -> str:
        return f'{self.country.name}, {self.name}'

class Street(Base):
    __tablename__ = 'street'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(ForeignKey('city.id'))
    name: Mapped[str] = mapped_column(String(50))

    city: Mapped['City'] = relationship(back_populates='streets')
    addresses: Mapped[list['Address']] = relationship(back_populates='street')

    @classmethod
    def get_or_create(cls, session: Session, street_name: str, city_name: str,
                      country_name: str) -> Self:
        city = City.get_or_create(session, city_name, country_name)
        street = session.query(Street) \
            .filter(Street.name == street_name, Street.city == city).first()
        if street is None:
            logger.debug('Creating new \'Street\' instance (name=\'%s\', '
                         'city=\'%s\')', street_name, city.full)
            street = Street(name=street_name, city=city)
            session.add(street)
        return street

    @property
    def full(self) -> str:
        return f'{self.city.full}, {self.name}'

class Address(Base):
    __tablename__ = 'address'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    street_id: Mapped[int] = mapped_column(ForeignKey('street.id'))
    house: Mapped[int]

    street: Mapped['Street'] = relationship(back_populates='addresses')

    @classmethod
    def get_or_create(cls, session: Session, address: _.Address) -> Self:
        street = Street.get_or_create(session, address.street,
                                      address.city, address.country)
        addr = session.query(Address) \
            .filter(Address.house == address.house, Address.street == street) \
            .first()
        if addr is None:
            logger.debug('Creating new \'Address\' instance (house=%i, '
                         'street=\'%s\')', address.house, street.full)
            addr = Address(house=address.house, street=street)
            session.add(addr)
        return addr

    @property
    def full(self) -> str:
        return f'{self.street.full} {self.house}'
