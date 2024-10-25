from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.Opportunity import opportunity
from models.User import  user, usercvs
from models.Additional import addressScheme, countryScheme, phonenumberScheme
from models.BaseModel import Base

import dbconfig as DB

engine = create_engine(
    f"postgresql+psycopg2://{DB.USERNAME}:{DB.PASSWORD}@localhost/{DB.NAME}", 
    echo=True, pool_size=6, max_overflow=10
)
engine.connect()

print(engine)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
session.close()