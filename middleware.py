"""Module with functions shared across API & UI or functions operating on internal types.
   Functions in this module doesn't check for operation permissions, it should be checked on caller side."""

from datetime import datetime, timedelta, UTC

from sqlalchemy.orm import Session

from utils import *
import db as db
import serializers.mod as ser
import formatters.mod as fmt


def create_user(session: Session, credentials: ser.User.Credentials) -> db.User | fmt.ErrorTrace:
    """Function for creating users. Returns newly created User instance on success.
       Otherwise, returns dictionary with field errors. Session don't have to be rolled back on failure.
       Http error status code - 422."""

    user = db.User.create(session, credentials)
    if not isinstance(user, db.User):
        return fmt.CreateUserFormatter.format_db_errors([user])
    return user

def authorize_user(session: Session, request: ser.User.Login) -> db.PersonalAPIKey | None:
    """Function for authorizing users. Returns newly created PersonalAPIKey on success.
       Otherwise, returns None. Session don't have to be rolled back on failure. Http error status code - 401."""

    user = db.User.login(session, request)
    if user is None:
        return
    expiry_date = datetime.now(UTC) + (timedelta(days=365) if request.remember_me else timedelta(hours=2))
    return db.PersonalAPIKey.generate(session, user, request.ip, expiry_date)

def update_user_info(session: Session, user: db.User, fields: ser.UserInfo.Update) -> None:
    """Function for updating regular user info. Can't fail in current implementation."""

    user.user_info.update(session, fields)

def validate_filter(session: Session, filter: ser.Opportunity.Filter) \
        -> tuple[list[db.OpportunityProvider], list[db.OpportunityTag], list[db.OpportunityGeoTag]] | fmt.ErrorTrace:
    """Function for validating opportunity filter. Returns tuple with database filter entites on success.
       Otherwise, returns dictionary with field errors. Session don't have to be rolled back on failure."""

    errors: list[GenericError[fmt.FilterOpportunitiesFormatter.ErrorCode, int]] = []
    providers: list[db.OpportunityProvider] = []
    for index, provider_id in enumerate(filter.provider_ids):
        provider: db.OpportunityProvider | None = session.get(db.OpportunityProvider, provider_id)
        if provider is None:
            errors.append(
                fmt.GetOpportunityProviderByID.create_db_error(
                    error_code=fmt.FilterOpportunitiesFormatter.ErrorCode.INVALID_PROVIDER_ID,
                    context=index)
            )
        else:
            providers.append(provider)
    tags: list[db.OpportunityTag] = []
    for index, tag_id in enumerate(filter.tag_ids):
        tag: db.OpportunityTag | None = session.get(db.OpportunityTag, tag_id)
        if tag is None:
            errors.append(
                fmt.GetOpportunityTagByID.create_db_error(
                    error_code=fmt.FilterOpportunitiesFormatter.ErrorCode.INVALID_TAG_ID,
                    context=index)
            )
        else:
            tags.append(tag)
    geo_tags: list[db.OpportunityGeoTag] = []
    for index, geo_tag_id in enumerate(filter.geo_tag_ids):
        geo_tag: db.OpportunityGeoTag | None = session.get(db.OpportunityGeoTag, geo_tag_id)
        if geo_tag is None:
            errors.append(
                fmt.GetOpportunityGeoTagByID.create_db_error(
                    error_code=fmt.FilterOpportunitiesFormatter.ErrorCode.INVALID_GEO_TAG_ID,
                    context=index)
            )
        else:
            geo_tags.append(geo_tag)
    if len(errors) > 0:
        return fmt.FilterOpportunitiesFormatter.format_db_errors(errors)
    return providers, tags, geo_tags

def filter_opportunities(session: Session, criteria: ser.Opportunity.Filter, *, public: bool = True) \
        -> list[db.Opportunity] | fmt.ErrorTrace:
    """Function for filtering opportunities. Returns sequence of opportunities on success.
       Otherwise, returns dictionary with field errors. Session don't have to be rolled back on failure.
       Http error status code - 422."""

    filter = validate_filter(session, criteria)
    if not isinstance(filter, tuple):
        return filter
    return db.Opportunity.filter(session, providers=filter[0], tags=filter[1], geo_tags=filter[2], page=criteria.page,
                                 public=public)

def create_opportunity_response(session: Session, user: db.User, opportunity: db.Opportunity,
                                data: ser.OpportunityResponse.CreateFields) -> db.OpportunityResponse | fmt.ErrorTrace:
    """Function for submitting data to opportunity form. Returns newly created OpportunityResponse instance on success.
       Otherwise, returns dictionary with field errors. Session must be rolled back on failure.
       Http error status code - 422."""

    form = opportunity.get_form()
    if form is None:
        return fmt.CreateOpportunityResponseFormatter.get_opportunity_no_form_error()
    if any(response.opportunity_id == opportunity.id for response in user.responses):
        return fmt.CreateOpportunityResponseFormatter.get_already_responded_error()
    response = db.OpportunityResponse.create(session, user, opportunity, form, data)
    if not isinstance(response, db.OpportunityResponse):
        return fmt.UpdateOpportunityFormFieldsFormatter.format_db_errors(response)
    # TODO: call submit method
    return response
