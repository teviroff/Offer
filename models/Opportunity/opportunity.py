from typing import Self
from enum import IntEnum
from dataclasses import dataclass

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import (
    Session, Mapped, mapped_column, relationship, object_session
)

from utils import *
from models.base import Base, FileURI, file_uri
from models.auxillary.address import City
from models.opportunity import response
import models.dataclasses as _

import logging

logger = logging.getLogger('database')

class CreateOpportunityErrorCode(IntEnum):
    INVALID_PROVIDER_ID = 0

class FilterOpportunityErrorCode(IntEnum):
    INVALID_TAG_ID = 0
    INVALID_GEO_TAG_ID = 1

class AddOpportunityTagErrorCode(IntEnum):
    INVALID_TAG_ID = 0

class Opportunity(Base):
    __tablename__ = 'opportunity'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    provider_id: Mapped[int] = \
        mapped_column(ForeignKey('opportunity_provider.id'))
    description: Mapped[file_uri] = mapped_column(FileURI)
    # might change to uri into NoSQL db
    required_data: Mapped[file_uri] = mapped_column(FileURI)

    provider: Mapped['OpportunityProvider'] = \
        relationship(back_populates='opportunities')
    tags: Mapped[list['OpportunityTag']] = \
        relationship(secondary='opportunity_to_tag',
                     back_populates='opportunities')
    geo_tags: Mapped[list['OpportunityGeoTag']] = \
        relationship(secondary='opportunity_to_geo_tag',
                     back_populates='opportunities')
    cards: Mapped[list['OpportunityCard']] = \
        relationship(back_populates='opportunity')
    responses: Mapped[list['response.OpportunityResponse']] = \
        relationship(back_populates='opportunity')

    @classmethod
    def create(cls, session: Session, fields: _.Opportunity) \
            -> Self | GenericError[CreateOpportunityErrorCode]:
        provider: OpportunityProvider | None = \
            session.query(OpportunityProvider).get(fields.provider_id)
        if provider is None:
            logger.debug('\'Opportunity.create\' exited with \'INVALID_PROVIDER_ID\' '
                         'error (id=%i)', fields.provider_id)
            return GenericError(
                error_code=CreateOpportunityErrorCode.INVALID_PROVIDER_ID,
                error_message='Opportunity provider with given id doesn\'t exist',
            )
        opportunity = Opportunity(
            name=fields.name,
            provider=provider,
            description=fields.description,
            required_data=fields.required_data,
        )
        session.add(opportunity)
        return opportunity

    @classmethod
    def filter(cls, session: Session, request: _.SearchRequest) \
            -> list[Self] | GenericError[FilterOpportunityErrorCode]:
        ...  # TODO

    def add_tag(self, session: Session, tag_id: int) \
            -> None | GenericError[AddOpportunityTagErrorCode]:
        tag: OpportunityTag | None = session.query(OpportunityTag).get(tag_id)
        if tag is None:
            logger.debug('\'Opportunity.add_tag\' exited with \'INVALID_TAG_ID\' '
                         'error (id=%i, tag_id=%i)', self.id, tag_id)
            return GenericError(
                error_code=AddOpportunityTagErrorCode.INVALID_TAG_ID,
                error_message='Opportunity tag with given id doesn\'t exist',
            )
        self.tags.append(tag)
    
    def add_geo_tag(self, session: Session, geo_tag_id: int) \
            -> None | GenericError[AddOpportunityTagErrorCode]:
        geo_tag: OpportunityGeoTag | None = \
            session.query(OpportunityGeoTag).get(geo_tag_id)
        if geo_tag is None:
            logger.debug('\'Opportunity.add_geo_tag\' exited with \'INVALID_TAG_ID\' '
                         'error (id=%i, geo_tag_id=%i)', self.id, geo_tag_id)
            return GenericError(
                error_code=AddOpportunityTagErrorCode.INVALID_TAG_ID,
                error_message='Opportunity geo tag with given id doesn\'t exist',
            )
        self.geo_tags.append(geo_tag)

class OpportunityProvider(Base):
    __tablename__ = 'opportunity_provider'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    logo: Mapped[file_uri] = mapped_column(FileURI, nullable=True)

    opportunities: Mapped[list['Opportunity']] = \
        relationship(back_populates='provider')

    @classmethod
    def create(cls, session: Session, fields: _.OpportunityProvider) -> Self:
        provider = OpportunityProvider(name=fields.name, logo=fields.logo)
        session.add(provider)
        return provider

    def update_logo(self, new_logo: file_uri) -> None:
        self.logo = new_logo

class CreateOpportunityTagErrorCode(IntEnum):
    NON_UNIQUE_NAME = 0

class OpportunityTag(Base):
    __tablename__ = 'opportunity_tag'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    opportunities: Mapped[list['Opportunity']] = \
        relationship(secondary='opportunity_to_tag', back_populates='tags')

    @classmethod
    def create(cls, session: Session, fields: _.OpportunityTag) \
            -> Self | GenericError[CreateOpportunityTagErrorCode]:
        tag = session.query(OpportunityTag) \
            .filter(OpportunityTag.name == fields.name).first()
        if tag is not None:
            logger.debug('\'OpportunityTag.create\' exited with \'NON_UNIQUE_NAME\' '
                         'error (name=\'%s\')', fields.name)
            return GenericError(
                error_code=CreateOpportunityTagErrorCode.NON_UNIQUE_NAME,
                error_message='Tag with given name already exists',
            )
        tag = OpportunityTag(name=fields.name)
        session.add(tag)
        return tag

class CreateOpportunityGeoTagErrorCode(IntEnum):
    INVALID_CITY_ID = 0
    NON_UNIQUE_CITY = 1

class OpportunityGeoTag(Base):
    __tablename__ = 'opportunity_geo_tag'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(ForeignKey('city.id'), unique=True)

    city: Mapped['City'] = relationship()
    opportunities: Mapped[list['Opportunity']] = \
        relationship(secondary='opportunity_to_geo_tag',
                     back_populates='geo_tags')

    @classmethod
    def create(cls, session: Session, city_id: int) \
            -> Self | GenericError[CreateOpportunityGeoTagErrorCode]:
        city: City | None = session.query(City).get(city_id)
        if city is None:
            logger.debug('\'OpportunityGeoTag.create\' exited with '
                         '\'INVALID_CITY_ID\' error (id=%i)', city_id)
            return GenericError(
                error_code=CreateOpportunityGeoTagErrorCode.INVALID_CITY_ID,
                error_message='City with given id doesn\'t exist',
            )
        geo_tag = session.query(OpportunityGeoTag) \
            .filter(OpportunityGeoTag.city == city).first()
        if geo_tag is not None:
            logger.debug('\'OpportunityGeoTag.create\' exited with '
                         '\'NON_UNIQUE_CITY\' error (city_id=%i)', city_id)
            return GenericError(
                error_code=CreateOpportunityGeoTagErrorCode.NON_UNIQUE_CITY,
                error_message='Geo tag with given city_id already exist',
            )
        geo_tag = OpportunityGeoTag(city=city)
        session.add(geo_tag)
        return geo_tag

class OpportunityToTag(Base):
    __tablename__ = 'opportunity_to_tag'

    opportunity_id: Mapped[int] = \
        mapped_column(ForeignKey('opportunity.id'), primary_key=True)
    tag_id: Mapped[int] = \
        mapped_column(ForeignKey('opportunity_tag.id'), primary_key=True)

class OpportunityToGeoTag(Base):
    __tablename__ = 'opportunity_to_geo_tag'

    opportunity_id: Mapped[int] = \
        mapped_column(ForeignKey('opportunity.id'), primary_key=True)
    geo_tag_id: Mapped[int] = \
        mapped_column(ForeignKey('opportunity_geo_tag.id'), primary_key=True)

class CreateOpportunityCardErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 0

class OpportunityCard(Base):
    __tablename__ = 'opportunity_card'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey('opportunity.id'))
    title: Mapped[str] = mapped_column(String(30))
    sub_title: Mapped[str | None] = mapped_column(String(30), nullable=True)

    opportunity: Mapped['Opportunity'] = relationship(back_populates='cards')

    @classmethod
    def create(cls, session: Session, fields: _.OpportunityCard) -> Self:
        opportunity: Opportunity | None = \
            session.query(Opportunity).get(fields.opportunity_id)
        if opportunity is None:
            logger.debug('\'OpportunityCard.create\' exited with '
                         '\'INVALID_OPPORTUNITY_ID\' error (opportunity_id=%i)',
                         fields.opportunity_id)
            return GenericError(
                error_code=CreateOpportunityCardErrorCode.INVALID_OPPORTUNITY_ID,
                error_message='Opportunity with given id doesn\'t exist',
            )
        card = OpportunityCard(opportunity=opportunity, title=fields.title,
                               sub_title=fields.sub_title)
        session.add(card)
        return card
