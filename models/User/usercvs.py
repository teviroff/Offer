import datetime
from sqlalchemy import Column, DateTime, Integer, String, create_engine, ForeignKey
import sqlalchemy
from ..BaseModel import Base

class UserCVS(Base):
    __tablename__ = 'user_cvs'
    ID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey('user.ID'))
    file = Column(String(128))
