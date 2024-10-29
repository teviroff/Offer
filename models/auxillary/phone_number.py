from typing import Self
from enum import IntEnum
from dataclasses import dataclass

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from models.base import Base
from models.auxillary.address import Country
import models.dataclasses as _

import logging

logger = logging.getLogger('database')

class CreatePhoneNumberErrorCode(IntEnum):
    INVALID_COUNTRY_ID = 0

@dataclass
class CreatePhoneNumberError:
    error_code: CreatePhoneNumberErrorCode
    error_message: str

class PhoneNumber(Base):
    __tablename__ = 'phone_number'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id'))
    number: Mapped[str] = mapped_column(String(10))

    country: Mapped['Country'] = relationship()

    @classmethod
    def create(cls, session: Session, fields: _.PhoneNumber) -> Self | CreatePhoneNumberError:
        country: Country | None = \
            session.query(Country).get(fields.country_id)
        if country is None:
            logger.debug('\'PhoneNumber.create\' exited with \'INVALID_COUNTRY_ID\' '
                         'error (id=%i)', fields.country_id)
            return CreatePhoneNumberError(
                error_code=CreatePhoneNumberErrorCode.INVALID_COUNTRY_ID,
                error_message='Country with provided id doesn\'t exist',
            )
        if country.phone_code is None:
            logger.warning('\'PhoneNumber.create\' called on \'Country\' with no '
                           'phone code (country_id=%i)', fields.country_id)
        phone_number = PhoneNumber(country=country, number=fields.number)
        session.add(phone_number)
        return phone_number

    @classmethod
    def get_or_create(cls, session: Session, fields: _.PhoneNumber) -> Self | CreatePhoneNumberError:
        phone_number = session.query(PhoneNumber) \
            .filter(PhoneNumber.country_id == fields.country_id,
                    PhoneNumber.number == fields.number) \
            .first()
        return phone_number if phone_number is not None \
            else cls.create(session, fields)

    @hybrid_property
    def full(self) -> str:
        return f'{self.country.phone_code}{self.number}'