import datetime
from sqlalchemy import Column, DateTime, Integer, String, create_engine, ForeignKey
import sqlalchemy
from sqlalchemy.orm import relationship

from ..BaseModel import Base

class User(Base):
    __tablename__ = 'user'
    ID = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    birthday = Column(DateTime, default=datetime.datetime.now)
    addressID = Column(Integer)
    avatar = Column(String(128))
    credentials = relationship("UserCredentials", uselist=False, backref="user")

class UserCredentials(Base):
    __tablename__ = 'user_credentials'
    ID = Column(Integer, primary_key=True)
    email = Column(String(30))
    passwordHash = Column(String(256))
    phoneNumberID = Column(Integer, ForeignKey('phone_number.ID'))
    userID = Column(Integer, ForeignKey('user.ID'))
