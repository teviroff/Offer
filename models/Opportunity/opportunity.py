import datetime
from sqlalchemy import Column, DateTime, Integer, String, create_engine, ForeignKey
import sqlalchemy

from ..BaseModel import Base

class Opportunity(Base):
    __tablename__ = 'opportunity'
    ID = Column(Integer, primary_key=True)
    name = Column(String(50))
    providerID = Column(Integer, ForeignKey('opportunity_provider.ID'))
    descriptionFile = Column(String(128))
    requiredData = Column(String(128))

class OpportunityTags(Base):
    __tablename__ = 'opportunity_tags'
    ID = Column(Integer, primary_key=True)
    name = Column(String(20))

class OpportunityToTags(Base):
    __tablename__ = 'opportunity_to_tags'
    ID = Column(Integer, primary_key=True)
    opportunityID = Column(Integer, ForeignKey('opportunity.ID'))
    tagID = Column(Integer, ForeignKey('opportunity_tags.ID'))

class OpportunityResponse(Base):
    __tablename__ = 'opportunity_response'
    ID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey('user.ID'))
    opportunityID = Column(Integer, ForeignKey('opportunity.ID'))
    responseData = Column(Integer)

class HistoryEntry(Base):
    __tablename__ = 'history_entry'
    ID = Column(Integer, primary_key=True)
    status = Column(String(10))
    description = Column(String(256))
    date = Column(DateTime, default=datetime.datetime.now)

class ResponseHistoryEntry(Base):
    __tablename__ = 'response_history_entry'
    ID = Column(Integer, primary_key=True)
    responseID = Column(Integer, ForeignKey('opportunity_response.ID'))
    entryID = Column(Integer, ForeignKey('history_entry.ID'))

class OpportunityCard(Base):
    __tablename__ = 'opportunity_card'
    ID = Column(Integer, primary_key=True)
    opportunityID = Column(Integer, ForeignKey('opportunity.ID'))
    layoutType = Column(Integer, default=1)
    descriptiion = Column(String(256))
    image = Column(String(128))

class OpportunityProvider(Base):
    __tablename__ = 'opportunity_provider'
    ID = Column(Integer, primary_key=True)
    name = Column(String(20))
    logo = Column(String(128))

class OpportunityToAddress(Base):
    __tablename__ = 'opportunity_to_address'
    ID = Column(Integer, primary_key=True)
    opportunityID = Column(Integer, ForeignKey('opportunity.ID'))
    addressID = Column(Integer, ForeignKey('address.ID'))