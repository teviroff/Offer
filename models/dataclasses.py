from typing import Self, Any
from dataclasses import dataclass

from models.base import file_uri

@dataclass
class Date:
    day: int
    month: int
    year: int

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class Address:
    country: str
    city: str
    street: str
    house: int

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class PhoneNumber:
    country_id: int
    number: str

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class UserCredentials:
    email: str
    password: str

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class UserInfo:
    name: str | None
    surname: str | None
    birthday: Date | None
    address: Address | None
    phone_number: PhoneNumber | None
    avatar: file_uri | None

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class Opportunity:
    name: str
    provider_id: int
    description: file_uri
    required_data: file_uri

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class SearchRequest:
    query: str | None
    tag_ids: list[int]
    geo_tag_ids: list[int]

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class OpportunityProvider:
    name: str
    logo: file_uri | None

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class OpportunityTag:
    name: str

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class OpportunityCard:
    opportunity_id: int
    ...  # TODO: figure out design

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class OpportunityResponse:
    user_id: int
    opportunity_id: int
    ...  # TODO: figure out NoSQL

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...

@dataclass
class ResponseStatus:
    response_id: int
    status: str
    description: str | None

    @classmethod
    def from_dict(cls, fields: dict[str, Any]) -> Self | None:
        ...
