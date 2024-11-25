from typing import BinaryIO
from dataclasses import dataclass

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship

import logging

logger = logging.getLogger('database')


class Base(DeclarativeBase):
    pass

# MongoDB aliases
MongoID = String(24)
mongo_id = str

@dataclass
class File:
    stream: BinaryIO
    size: int
