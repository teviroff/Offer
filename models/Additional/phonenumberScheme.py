import datetime
from sqlalchemy import Column, DateTime, Integer, String, create_engine, ForeignKey
import sqlalchemy

from ..BaseModel import Base

class Phonenumber(Base):
    __tablename__ = 'phone_number'
    ID = Column(Integer, primary_key=True)
    countryID = Column(Integer, ForeignKey('country.ID'))
    number = Column(String(10))
