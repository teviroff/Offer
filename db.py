from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.auxillary.address import Country, City
from models.auxillary.phone_number import PhoneNumber
from models.user import User, UserInfo, CV
from models.opportunity.opportunity import (
    Opportunity, OpportunityProvider, OpportunityTag, OpportunityGeoTag,
    OpportunityToTag, OpportunityToGeoTag, OpportunityCard
)
from models.opportunity.response import OpportunityResponse, ResponseStatus

import dbconfig as DB

def get_engine(user: str, password: str, host: str, 
               port: int, db_name: str) -> Engine:
    url = f'postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}'
    engine = create_engine(url)
    return engine

# run 'setup/dbconfig.bat' if you don't have dbconfig.py
engine = get_engine(DB.USERNAME, DB.PASSWORD, DB.HOST, DB.PORT, DB.NAME)
Session = sessionmaker(bind=engine)

# if you want to update shema, run following commands in interactive console:
# >>> from db import *
# >>> Base.metadata.drop_all(engine)
# >>> Base.metadata.create_all(engine)
# WARNING: you probably don't want to drop database with important data in it
