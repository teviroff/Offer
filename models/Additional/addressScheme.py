import datetime
from sqlalchemy import Column, DateTime, Integer, String, create_engine, ForeignKey
import sqlalchemy

from ..BaseModel import Base

class Address(Base):
    __tablename__ = 'address'
    ID = Column(Integer, primary_key=True)
    countryID = Column(Integer, ForeignKey('country.ID'))
    city = Column(String(20))
    street = Column(String(20))
    house = Column(Integer)
