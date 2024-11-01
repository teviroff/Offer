from typing import Self
from datetime import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship

from utils import *
from models.base import Base, FileURI, file_uri
from models.opportunity import opportunity as _opportunity
from models import user as _user
from models import dataclasses as _

import logging

logger = logging.getLogger('database')

class CreateResponseStatusErrorCode(IntEnum):
    INVALID_RESPONSE_ID = 0

class ResponseStatus(Base):
    __tablename__ = 'response_status'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    response_id: Mapped[int] = \
        mapped_column(ForeignKey('opportunity_response.id'))
    status: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    timestamp: Mapped[datetime]

    response: Mapped['OpportunityResponse'] = \
        relationship(back_populates='statuses')

    @classmethod
    def create_initial(cls, session: Session, response: 'OpportunityResponse') \
            -> Self:
        status = ResponseStatus(
            response=response,
            status='Response created',
            description=None,
            timestamp=datetime.now(),
        )
        session.add(status)
        return status

    @classmethod
    def create(cls, session: Session, fields: _.ResponseStatus) \
            -> Self | GenericError[CreateResponseStatusErrorCode]:
        response: OpportunityResponse | None = \
            session.query(OpportunityResponse).get(fields.response_id)
        if response is None:
            logger.debug('\'ResponseStatus.create\' exited with '
                         '\'INVALID_RESPONSE_ID\' error (id=%i)',
                         fields.response_id)
            return GenericError(
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

class CreateOpportunityResponseErrorCode(IntEnum):
    INVALID_USER_ID = 0
    INVALID_OPPORTUNITY_ID = 1

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
    def create(cls, session: Session, fields: _.OpportunityResponse) \
            -> Self | GenericError[CreateOpportunityResponseErrorCode]:
        user: _user.User | None = session.query(_user.User).get(fields.user_id)
        if user is None:
            logger.debug('\'OpportunityResponse.create\' exited with '
                         '\'INVALID_USER_ID\' error (user_id=%i)',
                         fields.user_id)
            return GenericError(
                error_code=CreateOpportunityResponseErrorCode.INVALID_USER_ID,
                error_message='User with given id doesn\'t exist',
            )
        opportunity: _opportunity.Opportunity | None = \
            session.query(_opportunity.Opportunity).get(fields.opportunity_id)
        if opportunity is None:
            logger.debug('\'OpportunityResponse.create\' exited with '
                         '\'INVALID_OPPORTUNITY_ID\' error (opportunity_id=%i)',
                         fields.opportunity_id)
            return GenericError(
                error_code=CreateOpportunityResponseErrorCode.INVALID_OPPORTUNITY_ID,
                error_message='User with given id doesn\'t exist',
            )
        response = OpportunityResponse(
            user=user,
            opportunity=opportunity,
            data=fields.data,
        )
        session.add(response)
        ResponseStatus.create_initial(session, response)
        return response
