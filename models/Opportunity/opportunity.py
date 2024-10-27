from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, FileURI, file_uri
from models.auxillary.address import City
from models.opportunity import response

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
        relationship(back_populates='opportunity_provider')
    tags: Mapped[list['OpportunityTag']] = \
        relationship(secondary='opportunity_to_tag',
                     back_populates='opportunities')
    geo_tags: Mapped[list['OpportunityGeoTag']] = \
        relationship(secondary='opportunity_to_geo_tag',
                     back_populates='opportunities')
    cards: Mapped[list['OpportunityCard']] = \
        relationship(back_populates='opportunity_card')
    responses: Mapped[list['response.OpportunityResponse']] = \
        relationship(back_populates='opportunity')

class OpportunityProvider(Base):
    __tablename__ = 'opportunity_provider'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    logo: Mapped[file_uri] = mapped_column(FileURI, nullable=True)

    opportunities: Mapped[list['Opportunity']] = \
        relationship(back_populates='opportunity')

class OpportunityTag(Base):
    __tablename__ = 'opportunity_tag'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))

    opportunities: Mapped[list['Opportunity']] = \
        relationship(secondary='opportunity_to_tag', back_populates='tags')

class OpportunityGeoTag(Base):
    __tablename__ = 'opportunity_geo_tag'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(ForeignKey('city.id'))

    city: Mapped['City'] = relationship()
    opportunities: Mapped[list['Opportunity']] = \
        relationship(secondary='opportunity_to_geo_tag',
                     back_populates='geo_tags')

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

class OpportunityCard(Base):
    __tablename__ = 'opportunity_card'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey('opportunity.id'))

    # TODO: end up on a concrete design and add corresponding columns

    opportunity: Mapped['Opportunity'] = \
        relationship(back_populates='opportunity')
