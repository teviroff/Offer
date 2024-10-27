from datetime import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, FileURI, file_uri
from models.opportunity import opportunity
from models import user

class OpportunityResponse(Base):
    __tablename__ = 'opportunity_response'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    opportunity_id: Mapped[int] = mapped_column(ForeignKey('opportunity.id'))
    data: Mapped[file_uri] = mapped_column(FileURI)  # see opportunity.py:15

    user: Mapped['user.User'] = relationship(back_populates='responses')
    opportunity: Mapped['opportunity.Opportunity'] = \
        relationship(back_populates='responses')
    statuses: Mapped[list['ResponseStatus']] = \
        relationship(back_populates='response')

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
