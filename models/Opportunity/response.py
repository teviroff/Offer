from typing import Self
from datetime import datetime
from enum import IntEnum
from dataclasses import dataclass

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship

from models.base import Base, FileURI, file_uri
from models.opportunity import opportunity as _opportunity
from models import user as _user
from models import dataclasses as _

import logging

logger = logging.getLogger('database')

class OpportunityResponse(Base):
    __tablename__ = 'opportunity_response'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    opportunity_id: Mapped[int] = mapped_column(ForeignKey('opportunity.id'))
    data: Mapped[file_uri] = mapped_column(FileURI)  # see opportunity.py:15

    user: Mapped['_user.User'] = relationship(back_populates='responses')
    opportunity: Mapped['_opportunity.Opportunity'] = \
        relationship(back_populates='responses')
    statuses: Mapped[list['ResponseStatus']] = \
        relationship(back_populates='response')

    @classmethod
    def create(cls, session: Session, fields: _.OpportunityResponse) -> Self:
        ...

class CreateResponseStatusErrorCode(IntEnum):
    INVALID_RESPONSE_ID = 0

@dataclass
class CreateResponseStatusError:
    error_code: CreateResponseStatusErrorCode
    error_message: str

class ResponseStatus(Base):
    __tablename__ = 'response_status'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    response_id: Mapped[int] = \
        mapped_column(ForeignKey('opportunity_response.id'))
    status: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    timestamp: Mapped[datetime]

    response: Mapped['OpportunityResponse'] = \
        relationship(back_populates='statuses')

    @classmethod
    def create(cls, session: Session, fields: _.ResponseStatus) -> Self | CreateResponseStatusError:
        response: OpportunityResponse | None = \
            session.query(OpportunityResponse).get(fields.response_id)
        if response is None:
            logger.debug('\'ResponseStatus.create\' exited with '
                         '\'INVALID_RESPONSE_ID\' error (id=%i)',
                         fields.response_id)
            return CreateResponseStatusError(
                error_code=CreateResponseStatusErrorCode.INVALID_RESPONSE_ID,
                error_message='Opportunity response with given id doesn\'t exist',
            )
        status = ResponseStatus(
            response=response,
            status=fields.status,
            description=fields.description,
            timestamp=datetime.now(),
        )
        session.add(status)
        return status
