from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from models.base import Base
from models.auxillary.address import Country

class PhoneNumber(Base):
    __tablename__ = 'phone_number'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id'))
    number: Mapped[str] = mapped_column(String(10))

    country: Mapped["Country"] = relationship()

    @hybrid_property
    def full(self) -> str:
        return f'{self.country.phone_code}{self.number}'
