from typing import Self

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship

from utils import *
from models.base import Base
import serializers.mod as ser

import logging

logger = logging.getLogger('database')

class CreateCountryErrorCode(IntEnum):
    NON_UNIQUE_NAME = 0

class Country(Base):
    __tablename__ = 'country'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    phone_code: Mapped[str] = mapped_column(String(3))

    cities: Mapped[list['City']] = relationship(back_populates='country')

    @classmethod
    def create(cls, session: Session, fields: ser.auxillary.Country) \
            -> Self | GenericError[CreateCountryErrorCode]:
        country = session.query(Country) \
            .filter(Country.name == fields.name).first()
        if country is not None:
            logger.debug('\'Country.create\' exited with \'NON_UNIQUE_NAME\' '
                         'error (name=\'%s\')', fields.name)
            return GenericError(
                error_code=CreateCountryErrorCode.NON_UNIQUE_NAME,
                error_message='Country with given name already exists'
            )
        country = Country(name=fields.name, phone_code=fields.phone_code)
        session.add(country)
        return country

class CreateCityErrorCode(IntEnum):
    INVALID_COUNTRY_ID = 0

class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id'))
    name: Mapped[str] = mapped_column(String(50))

    country: Mapped['Country'] = relationship(back_populates='cities')

    @classmethod
    def create(cls, session: Session, fields: ser.auxillary.City) \
            -> Self | GenericError[CreateCityErrorCode]:
        country: Country | None = session.query(Country).get(fields.country_id)
        if country is None:
            logger.debug('\'City.create\' exited with \'INVALID_COUNTRY_ID\' '
                         'error (country_id=%i)', fields.country_id)
            return GenericError(
                error_code=CreateCityErrorCode.INVALID_COUNTRY_ID,
                error_message='Country with provided if doesn\'t exist'
            )
        city = City(country=country, name=fields.name)
        session.add(city)
        return city

    @property
    def full(self) -> str:
        return f'{self.country.name}, {self.name}'
