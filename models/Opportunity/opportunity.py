from typing import Self, Union

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Session, Mapped, mapped_column, relationship

from utils import *
from models.base import Base, FileURI, file_uri
from models.auxillary.address import City
from models.opportunity import response
import serializers.mod as ser

import logging

logger = logging.getLogger('database')


class CreateOpportunityErrorCode(IntEnum):
    INVALID_PROVIDER_ID = 0

class FilterOpportunityErrorCode(IntEnum):
    INVALID_TAG_ID = 0
    INVALID_GEO_TAG_ID = 1

class AddOpportunityTagErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 0
    INVALID_TAG_ID = 1

class AddOpportunityGeoTagErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 0
    INVALID_GEO_TAG_ID = 1

class Opportunity(Base):
    __tablename__ = 'opportunity'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    provider_id: Mapped[int] = mapped_column(ForeignKey('opportunity_provider.id'))
    description: Mapped[str] = mapped_column(String(250))
    # TODO: required_data: Mapped[file_uri] = mapped_column(FileURI)

    provider: Mapped['OpportunityProvider'] = relationship(back_populates='opportunities')
    tags: Mapped[set['OpportunityTag']] = relationship(secondary='opportunity_to_tag', back_populates='opportunities')
    geo_tags: Mapped[set['OpportunityGeoTag']] = relationship(secondary='opportunity_to_geo_tag',
                                                              back_populates='opportunities')
    cards: Mapped[list['OpportunityCard']] = relationship(back_populates='opportunity')
    responses: Mapped[list['response.OpportunityResponse']] = relationship(back_populates='opportunity')

    @classmethod
    def create(cls, session: Session, request: ser.Opportunity.Create) \
            -> Self | GenericError[CreateOpportunityErrorCode]:
        provider: OpportunityProvider | None = session.query(OpportunityProvider).get(request.provider_id)
        if provider is None:
            logger.debug('\'Opportunity.create\' exited with \'INVALID_PROVIDER_ID\' '
                         'error (id=%i)', request.provider_id)
            return GenericError(
                error_code=CreateOpportunityErrorCode.INVALID_PROVIDER_ID,
                error_message='Opportunity provider with given id doesn\'t exist',
            )
        opportunity = Opportunity(name=request.name, provider=provider, description=request.description)
        session.add(opportunity)
        return opportunity

    # TODO
    @classmethod
    def filter(cls, session: Session, request: ser.Opportunity.Filter) \
            -> list[Self] | list[GenericError[FilterOpportunityErrorCode]]:
        ...

    @classmethod
    def add_tags(cls, session: Session, request: ser.Opportunity.AddTags) \
            -> None | list[GenericError[AddOpportunityTagErrorCode, int | None]]:
        opportunity: Opportunity | None = session.query(Opportunity).get(request.opportunity_id)
        if opportunity is None:
            logger.debug('\'Opportunity.add_tags\' exited with \'INVALID_OPPORTUNITY_ID\' error (opportunity_id=%i)',
                         request.opportunity_id)
            return [GenericError(error_code=AddOpportunityTagErrorCode.INVALID_OPPORTUNITY_ID,
                                 error_message='Opportunity with provided id doesn\'t exist')]
        tag_errors: list[GenericError[AddOpportunityTagErrorCode, int]] = []
        for i, tag_id in enumerate(request.tag_ids):
            tag: Union['OpportunityTag', None] = session.query(OpportunityTag).get(tag_id)
            if tag is None:
                logger.debug('\'Opportunity.add_tags\' generated \'INVALID_TAG_ID\' error (opportunity_id=%i, '
                             'tag_id=%i)', request.opportunity_id, tag_id)
                tag_errors.append(
                    GenericError(error_code=AddOpportunityTagErrorCode.INVALID_TAG_ID,
                                 error_message='Opportunity tag with provided id doesn\'t exist', context=i)
                )
                continue
            opportunity.tags.add(tag)
        if len(tag_errors) > 0:
            return tag_errors

    @classmethod
    def add_geo_tags(cls, session: Session, request: ser.Opportunity.AddGeoTags) \
            -> None | list[GenericError[AddOpportunityGeoTagErrorCode, int | None]]:
        opportunity: Opportunity | None = session.query(Opportunity).get(request.opportunity_id)
        if opportunity is None:
            logger.debug('\'Opportunity.add_geo_tags\' exited with \'INVALID_OPPORTUNITY_ID\' error '
                         '(opportunity_id=%i)', request.opportunity_id)
            return [GenericError(error_code=AddOpportunityGeoTagErrorCode.INVALID_OPPORTUNITY_ID,
                                 error_message='Opportunity with provided id doesn\'t exist')]
        tag_errors: list[GenericError[AddOpportunityGeoTagErrorCode, int]] = []
        for i, tag_id in enumerate(request.geo_tag_ids):
            tag: Union['OpportunityGeoTag', None] = session.query(OpportunityGeoTag).get(tag_id)
            if tag is None:
                logger.debug('\'Opportunity.add_geo_tags\' generated \'INVALID_GEO_TAG_ID\' error (opportunity_id=%i, '
                             'geo_tag_id=%i)', request.opportunity_id, tag_id)
                tag_errors.append(
                    GenericError(error_code=AddOpportunityGeoTagErrorCode.INVALID_GEO_TAG_ID,
                                 error_message='Opportunity geo tag with provided id doesn\'t exist', context=i)
                )
                continue
            opportunity.geo_tags.add(tag)
        if len(tag_errors) > 0:
            return tag_errors

    @classmethod
    def get_dict(cls, session: Session, opportunity_id: int) -> dict | None:
        opportunity: Opportunity | None = session.query(Opportunity).get(opportunity_id)
        if opportunity is None:
            return
        return {
            'name': opportunity.name,
            'provider': {'name': opportunity.provider.name},
            'tags': [{'name': tag.name} for tag in opportunity.tags],
            'geo_tags': [{'city_name': geo_tag.city.name} for geo_tag in opportunity.geo_tags],
            'description': opportunity.description,
        }


class OpportunityProvider(Base):
    __tablename__ = 'opportunity_provider'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    logo: Mapped[file_uri | None] = mapped_column(FileURI, nullable=True)

    opportunities: Mapped[list['Opportunity']] = relationship(back_populates='provider')

    @classmethod
    def create(cls, session: Session, request: ser.OpportunityProvider.Create) -> Self:
        provider = OpportunityProvider(name=request.name)
        session.add(provider)
        return provider

    # TODO
    @classmethod
    def update_logo(cls, session: Session, request: ser.OpportunityProvider.UpdateLogo) -> None:
        ...


class CreateOpportunityTagErrorCode(IntEnum):
    NON_UNIQUE_NAME = 0

class OpportunityTag(Base):
    __tablename__ = 'opportunity_tag'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    opportunities: Mapped[list['Opportunity']] = relationship(secondary='opportunity_to_tag', back_populates='tags')

    @classmethod
    def create(cls, session: Session, request: ser.OpportunityTag.Create) \
            -> Self | GenericError[CreateOpportunityTagErrorCode]:
        tag = session.query(OpportunityTag).filter(OpportunityTag.name == request.name).first()
        if tag is not None:
            logger.debug('\'OpportunityTag.create\' exited with \'NON_UNIQUE_NAME\' error (name=\'%s\')', request.name)
            return GenericError(
                error_code=CreateOpportunityTagErrorCode.NON_UNIQUE_NAME,
                error_message='Tag with given name already exists',
            )
        tag = OpportunityTag(name=request.name)
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
    opportunities: Mapped[list['Opportunity']] = relationship(secondary='opportunity_to_geo_tag',
                                                              back_populates='geo_tags')

    @classmethod
    def create(cls, session: Session, request: ser.OpportunityGeoTag.Create) \
            -> Self | GenericError[CreateOpportunityGeoTagErrorCode]:
        city: City | None = session.query(City).get(request.city_id)
        if city is None:
            logger.debug('\'OpportunityGeoTag.create\' exited with \'INVALID_CITY_ID\' error (id=%i)', request.city_id)
            return GenericError(
                error_code=CreateOpportunityGeoTagErrorCode.INVALID_CITY_ID,
                error_message='City with given id doesn\'t exist',
            )
        geo_tag = session.query(OpportunityGeoTag).filter(OpportunityGeoTag.city == city).first()
        if geo_tag is not None:
            logger.debug('\'OpportunityGeoTag.create\' exited with \'NON_UNIQUE_CITY\' error (city_id=%i)',
                         request.city_id)
            return GenericError(
                error_code=CreateOpportunityGeoTagErrorCode.NON_UNIQUE_CITY,
                error_message='Geo tag with given city_id already exist',
            )
        geo_tag = OpportunityGeoTag(city=city)
        session.add(geo_tag)
        return geo_tag


class OpportunityToTag(Base):
    __tablename__ = 'opportunity_to_tag'

    opportunity_id: Mapped[int] = mapped_column(ForeignKey('opportunity.id'), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey('opportunity_tag.id'), primary_key=True)


class OpportunityToGeoTag(Base):
    __tablename__ = 'opportunity_to_geo_tag'

    opportunity_id: Mapped[int] = mapped_column(ForeignKey('opportunity.id'), primary_key=True)
    geo_tag_id: Mapped[int] = mapped_column(ForeignKey('opportunity_geo_tag.id'), primary_key=True)


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
    def create(cls, session: Session, request: ser.OpportunityCard.Create) \
            -> Self | GenericError[CreateOpportunityCardErrorCode]:
        opportunity: Opportunity | None = session.query(Opportunity).get(request.opportunity_id)
        if opportunity is None:
            logger.debug('\'OpportunityCard.create\' exited with \'INVALID_OPPORTUNITY_ID\' error (opportunity_id=%i)',
                         request.opportunity_id)
            return GenericError(
                error_code=CreateOpportunityCardErrorCode.INVALID_OPPORTUNITY_ID,
                error_message='Opportunity with given id doesn\'t exist',
            )
        card = OpportunityCard(opportunity=opportunity, title=request.title, sub_title=request.sub_title)
        session.add(card)
        return card
