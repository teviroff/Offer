from typing import NewType

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Type aliases for consistency
FileURI = String(128)
file_uri = str
