from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mongoengine import connect
from minio import Minio

from models.base import Base, File
from models.auxillary.address import Country, City
from models.auxillary.phone_number import PhoneNumber
from models.user import (
    PersonalAPIKey, DeveloperAPIKey, APIKey, User, UserInfo, CV
)
from models.opportunity.opportunity import (
    Opportunity, OpportunityProvider, OpportunityTag, OpportunityGeoTag,
    OpportunityToTag, OpportunityToGeoTag, OpportunityCard
)
from mongo_models.opportunity_fields import (
    OpportunityForm, FieldType as OpportunityFieldType,
)
from models.opportunity.response import OpportunityResponse, ResponseStatus

import dbconfig as dbcfg

def get_pg_engine(user: str, password: str, host: str, port: int, db_name: str):
    return create_engine(f'postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}')

def connect_mongo_db(user: str, password: str, host: str, port: int, db_name: str):
    connect(host=f'mongodb://{user}:{password}@{host}:{port}/{db_name}')

# TODO: figure out cerificates
def get_minio_client(access_key: str, secret_key: str, host: str, port: int):
    return Minio(f'{host}:{port}', access_key=access_key, secret_key=secret_key, secure=False)

# run 'setup/dbconfig.bat' if you don't have dbconfig.py
pg_engine = get_pg_engine(
    user=dbcfg.PG_USERNAME,
    password=dbcfg.PG_PASSWORD,
    host=dbcfg.PG_HOST,
    port=dbcfg.PG_PORT,
    db_name=dbcfg.PG_DB_NAME,
)
connect_mongo_db(
    user=dbcfg.MONGO_USERNAME,
    password=dbcfg.MONGO_PASSWORD,
    host=dbcfg.MONGO_HOST,
    port=dbcfg.MONGO_PORT,
    db_name=dbcfg.MONGO_DB_NAME,
)
minio_client = get_minio_client(
    access_key=dbcfg.MINIO_ACCESS_KEY,
    secret_key=dbcfg.MINIO_SECRET_KEY,
    host=dbcfg.MINIO_HOST,
    port=dbcfg.MINIO_PORT,
)

Session = sessionmaker(bind=pg_engine)

# if you want to update postgres schema, run following commands in interactive console:
# >>> from db import *
# >>> Base.metadata.drop_all(pg_engine)
# >>> Base.metadata.create_all(pg_engine)
# WARNING: you probably don't want to drop database with important data in it
