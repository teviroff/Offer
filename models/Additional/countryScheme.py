import datetime
from sqlalchemy import Column, DateTime, Integer, String, create_engine, ForeignKey
import sqlalchemy

from ..BaseModel import Base

class CountryScheme(Base):
    __tablename__ = "country"
    ID = Column(Integer, primary_key=True)
    name = Column(String(20))
    code = Column(String(2))
    phoneCode = Column(Integer)
