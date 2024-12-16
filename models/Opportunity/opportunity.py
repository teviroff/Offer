from typing import Any, Collection, Self, Union

from minio import Minio, S3Error
from sqlalchemy import select, func

from utils import *
from models.base import *
from models.auxillary.address import City
from models.opportunity import response
from mongo_models.opportunity_fields import OpportunityForm
import serializers.mod as ser

import logging

logger = logging.getLogger('database')


class CreateOpportunityErrorCode(IntEnum):
    INVALID_PROVIDER_ID = 0

class AddOpportunityTagErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 0
    INVALID_TAG_ID = 1

class AddOpportunityGeoTagErrorCode(IntEnum):
    INVALID_OPPORTUNITY_ID = 0
    INVALID_GEO_TAG_ID = 1

class Opportunity(Base):
    __tablename__ = 'opportunity'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    link: Mapped[str | None] = mapped_column(String(120), nullable=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey('opportunity_provider.id'))

    provider: Mapped['OpportunityProvider'] = relationship(back_populates='opportunities')
    tags: Mapped[set['OpportunityTag']] = relationship(secondary='opportunity_to_tag', back_populates='opportunities')
    geo_tags: Mapped[set['OpportunityGeoTag']] = relationship(secondary='opportunity_to_geo_tag',
                                                              back_populates='opportunities')
    card: Mapped['OpportunityCard'] = relationship(back_populates='opportunity', cascade='all, delete-orphan')
    responses: Mapped[list['response.OpportunityResponse']] = relationship(back_populates='opportunity',
                                                                           cascade='all, delete-orphan')

    @classmethod
    def create(cls, session: Session, fields: ser.Opportunity.Create) \
            -> Self | GenericError[CreateOpportunityErrorCode]:
        provider: OpportunityProvider | None = session.query(OpportunityProvider).get(fields.provider_id)
        if provider is None:
            logger.debug('\'Opportunity.create\' exited with \'INVALID_PROVIDER_ID\' '
                         'error (id=%i)', fields.provider_id)
            return GenericError(
                error_code=CreateOpportunityErrorCode.INVALID_PROVIDER_ID,
                error_message='Opportunity provider with given id doesn\'t exist',
            )
        opportunity = Opportunity(name=fields.name, link=fields.link, provider=provider)
        session.add(opportunity)
        return opportunity

    def get_form(self) -> OpportunityForm | None:
        return OpportunityForm.objects(id=self.id).first()

    @classmethod
    def filter(cls, session: Session, *, providers: Collection['OpportunityProvider'],
               tags: Collection['OpportunityTag'], geo_tags: Collection['OpportunityGeoTag'],
               page: int, public: bool = True) -> list['Opportunity']:
        statement = select(Opportunity)
        if len(providers) > 0:
            statement = statement.where(Opportunity.provider_id.in_(provider.id for provider in providers))
        if len(tags) > 0:
            substatement = select(OpportunityToTag.opportunity_id) \
                .where(OpportunityToTag.tag_id.in_(tag.id for tag in tags)) \
                .group_by(OpportunityToTag.opportunity_id) \
                .having(func.count(OpportunityToTag.tag_id) == len(tags))
            statement = statement.where(Opportunity.id.in_(substatement))
        if len(geo_tags) > 0:
            substatement = select(OpportunityToGeoTag.opportunity_id) \
                .where(OpportunityToGeoTag.geo_tag_id.in_(geo_tag.id for geo_tag in geo_tags)) \
                .group_by(OpportunityToGeoTag.opportunity_id) \
                .having(func.count(OpportunityToGeoTag.geo_tag_id) > 0)
            statement = statement.where(Opportunity.id.in_(substatement))
        if public:
            statement = statement.where(Opportunity.card != None)
        PAGE_SIZE: int = 12  # TODO: find better place for this constant
        statement = statement.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)
        return session.execute(statement).scalars().all()

    def add_tags(self, session: Session, fields: ser.Opportunity.AddTags) \
            -> None | list[GenericError[AddOpportunityTagErrorCode, int | None]]:
        tag_errors: list[GenericError[AddOpportunityTagErrorCode, int]] = []
        for i, tag_id in enumerate(fields.tag_ids):
            tag: Union['OpportunityTag', None] = session.query(OpportunityTag).get(tag_id)
            if tag is None:
                logger.debug('\'Opportunity.add_tags\' generated \'INVALID_TAG_ID\' error (opportunity_id=%i, '
                             'tag_id=%i)', self.id, tag_id)
                tag_errors.append(
                    GenericError(error_code=AddOpportunityTagErrorCode.INVALID_TAG_ID,
                                 error_message='Opportunity tag with provided id doesn\'t exist', context=i)
                )
                continue
            self.tags.add(tag)
        if len(tag_errors) > 0:
            return tag_errors

    def add_geo_tags(self, session: Session, fields: ser.Opportunity.AddGeoTags) \
            -> None | list[GenericError[AddOpportunityGeoTagErrorCode, int | None]]:
        tag_errors: list[GenericError[AddOpportunityGeoTagErrorCode, int]] = []
        for i, tag_id in enumerate(fields.geo_tag_ids):
            tag: Union['OpportunityGeoTag', None] = session.query(OpportunityGeoTag).get(tag_id)
            if tag is None:
                logger.debug('\'Opportunity.add_geo_tags\' generated \'INVALID_GEO_TAG_ID\' error (opportunity_id=%i, '
                             'geo_tag_id=%i)', fields.opportunity_id, tag_id)
                tag_errors.append(
                    GenericError(error_code=AddOpportunityGeoTagErrorCode.INVALID_GEO_TAG_ID,
                                 error_message='Opportunity geo tag with provided id doesn\'t exist', context=i)
                )
                continue
            self.geo_tags.add(tag)
        if len(tag_errors) > 0:
            return tag_errors

    def update_description(self, minio_client: Minio, file: File) -> None:
        """Method for updating opportunity description. Assumes 'file' is a valid Markdown file.
           Can't error in current implementation."""

        minio_client.put_object('opportunity-description', f'{self.id}.md', file.stream, file.size)

    def get_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'provider_id': self.provider.id,
            'provider_logo_url': self.provider.logo_url,
            'provider_name': self.provider.name,
            'tags': [(tag.id, tag.name) for tag in self.tags],
            'geo_tags': [(geo_tag.id, geo_tag.city.name) for geo_tag in self.geo_tags],
        }

    def get_description(self, minio_client: Minio) -> bytes:
        response = None
        try:
            response = minio_client.get_object('opportunity-description', f'{self.id}.md')
            description = response.read()
        except S3Error:
            response = minio_client.get_object('opportunity-description', 'default.md')
            description = response.read()
        finally:
            response.close()
            response.release_conn()
        return description

    def get_card_dict(self) -> dict[str, Any]:
        return {
            'opportunity_id': self.id,
            'provider_logo_url': self.provider.logo_url,
            'provider_name': self.provider.name,
            'card_title': self.card.title,
            'card_subtitle': self.card.subtitle,
            'tags': [(tag.id, tag.name) for tag in self.tags],
            'geo_tags': [(geo_tag.id, geo_tag.city.name) for geo_tag in self.geo_tags],
        }


class OpportunityProvider(Base):
    __tablename__ = 'opportunity_provider'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))

    opportunities: Mapped[list['Opportunity']] = relationship(back_populates='provider')

    @classmethod
    def create(cls, session: Session, fields: ser.OpportunityProvider.Create) -> Self:
        provider = OpportunityProvider(name=fields.name)
        session.add(provider)
        return provider

    @property
    def logo_url(self) -> str:
        return f'/api/opportunity-provider/logo/{self.id}'

    def get_logo(self, minio_client: Minio) -> bytes:
        response = None
        try:
            response = minio_client.get_object('opportunity-provider-logo', f'{self.id}.png')
            avatar = response.read()
        except S3Error:
            response = minio_client.get_object('opportunity-provider-logo', 'default.png')
            avatar = response.read()
        finally:
            response.close()
            response.release_conn()
        return avatar

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
    def create(cls, session: Session, fields: ser.OpportunityTag.Create) \
            -> Self | GenericError[CreateOpportunityTagErrorCode]:
        tag = session.query(OpportunityTag).filter(OpportunityTag.name == fields.name).first()
        if tag is not None:
            logger.debug('\'OpportunityTag.create\' exited with \'NON_UNIQUE_NAME\' error (name=\'%s\')', fields.name)
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
    opportunities: Mapped[list['Opportunity']] = relationship(secondary='opportunity_to_geo_tag',
                                                              back_populates='geo_tags')

    @classmethod
    def create(cls, session: Session, fields: ser.OpportunityGeoTag.Create) \
            -> Self | GenericError[CreateOpportunityGeoTagErrorCode]:
        city: City | None = session.query(City).get(fields.city_id)
        if city is None:
            logger.debug('\'OpportunityGeoTag.create\' exited with \'INVALID_CITY_ID\' error (id=%i)', fields.city_id)
            return GenericError(
                error_code=CreateOpportunityGeoTagErrorCode.INVALID_CITY_ID,
                error_message='City with given id doesn\'t exist',
            )
        geo_tag = session.query(OpportunityGeoTag).filter(OpportunityGeoTag.city == city).first()
        if geo_tag is not None:
            logger.debug('\'OpportunityGeoTag.create\' exited with \'NON_UNIQUE_CITY\' error (city_id=%i)',
                         fields.city_id)
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


class OpportunityCard(Base):
    __tablename__ = 'opportunity_card'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey('opportunity.id'))
    title: Mapped[str] = mapped_column(String(30))
    subtitle: Mapped[str | None] = mapped_column(String(30), nullable=True)

    opportunity: Mapped['Opportunity'] = relationship(back_populates='card')

    @classmethod
    def create(cls, session: Session, opportunity: Opportunity, fields: ser.OpportunityCard.Create) -> Self:
        card = OpportunityCard(opportunity=opportunity, title=fields.title, subtitle=fields.subtitle)
        session.add(card)
        return card
