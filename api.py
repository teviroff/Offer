from typing import Annotated, Iterable
from enum import IntEnum

from config import *
from fastapi import Path, Query, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import db as db
import serializers.mod as ser
import formatters.mod as fmt
import middleware as mw


def default_request_validation_error_handler_factory(
        error_formatter: Callable[[Iterable[fmt.PydanticError]], fmt.ErrorTrace]
) -> RequestValidationErrorHandler:
    def handler_fn(e: RequestValidationError) -> JSONResponse:
        return JSONResponse(error_formatter(e.errors()), status_code=422)

    return handler_fn


class GetDeveloperAPIKeyErrorCode(IntEnum):
    DOESNT_EXIST = 0
    NOT_DEVELOPER = 1

def get_developer_api_key(session: Session, key: ser.API_KEY) -> db.DeveloperAPIKey | GetDeveloperAPIKeyErrorCode:
    """Asserts that given API key exists and is developer."""

    api_key = db.APIKey.get(session, ser.APIKey.model_construct(key=key))
    if api_key is None:
        return GetDeveloperAPIKeyErrorCode.DOESNT_EXIST
    if not isinstance(api_key, db.DeveloperAPIKey):
        return GetDeveloperAPIKeyErrorCode.NOT_DEVELOPER
    return api_key

def get_developer_api_key_error() -> fmt.ErrorTrace:
    """Return dictionary with API key errors."""

    return fmt.GetAPIKeyFormatter.get_db_error()

def get_developer_api_key_error_response() -> JSONResponse:
    """Return JSON response with API key errors."""

    return JSONResponse(get_developer_api_key_error(), status_code=422)


def get_user_by_id(session: Session, user_id: ser.ID) -> db.User | None:
    """Get user by id. Returns None if user with provided id doesn't exist."""

    return session.get(db.User, user_id)

def get_user_by_id_error(code: int) -> fmt.ErrorTrace:
    """Return dictionary with user id errors."""

    return fmt.GetUserByIDFormatter.get_db_error(code=code)

def get_user_by_id_error_response(code: int) -> JSONResponse:
    """Return JSON response with usre id errors."""

    return JSONResponse(get_user_by_id_error(code), status_code=422)


@app.post('/api/private/user')
def create_user(credentials: ser.User.Credentials) -> JSONResponse:
    with db.Session.begin() as session:
        user = mw.create_user(session, credentials)
        if not isinstance(user, db.User):
            session.rollback()
            return JSONResponse(user, status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/private/user', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.CreateUserFormatter.format_serializer_errors)
)

@app.get('/api/user/avatar/{user_id}')
async def get_user_avatar(request: Request, user_id: Annotated[int, Path(ge=1)]):
    with db.Session.begin() as session:
        user = get_user_by_id(session, user_id)
        if user is None:
            return page_not_found_response(request)
        avatar = user.get_avatar(db.minio_client)
    return Response(avatar, media_type='image/png')

@app.patch('/api/user/info')
def update_user_info(
    query: Annotated[ser.User.QueryParameters, Query()],
    fields: ser.UserInfo.Update,
) -> JSONResponse:
    class ErrorCode(IntEnum):
        INVALID_USER_ID = 200

    with db.Session.begin() as session:
        api_key = get_developer_api_key(session, query.api_key)
        if not isinstance(api_key, db.DeveloperAPIKey):
            return get_developer_api_key_error_response()
        user = get_user_by_id(session, query.user_id)
        if user is None:
            return get_user_by_id_error_response(ErrorCode.INVALID_USER_ID)
        mw.update_user_info(session, user, fields)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/user/info', 'PATCH',
    handler=default_request_validation_error_handler_factory(fmt.UpdateUserInfoFormatter.format_serializer_errors)
)

# TODO
# @app.patch('/api/user/phone-number')
# def update_user_phone_number(request: ...) -> JSONResponse:
#     ...
#     return JSONResponse({})

# TODO: return id
@app.post('/api/private/opportunity-provider')
def create_opportunity_provider(request: ser.OpportunityProvider.Create) -> JSONResponse:
    with db.Session.begin() as session:
        api_key = get_developer_api_key(session, request.api_key)
        if not isinstance(api_key, db.DeveloperAPIKey):
            return get_developer_api_key_error_response()
        db.OpportunityProvider.create(session, request)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/private/opportunity-provider', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.CreateProviderFormatter.format_serializer_errors)
)

def get_opportunity_provider_by_id(session: Session, provider_id: ser.ID) -> db.OpportunityProvider | None:
    """Get opportunity provider by id. Returns None if provider with provided id doesn't exist."""

    return session.get(db.OpportunityProvider, provider_id)

@app.get('/api/opportunity-provider/logo/{provider_id}')
async def get_opportunity_provider_logo(request: Request, provider_id: Annotated[int, Path(ge=1)]):
    with db.Session.begin() as session:
        provider = get_opportunity_provider_by_id(session, provider_id)
        if provider is None:
            return page_not_found_response(request)
        avatar = provider.get_avatar(db.minio_client)
    return Response(avatar, media_type='image/png')


@app.post('/api/private/opportunity')
def create_opportunity(request: ser.Opportunity.Create) -> JSONResponse:
    with db.Session.begin() as session:
        api_key = get_developer_api_key(session, request.api_key)
        if not isinstance(api_key, db.DeveloperAPIKey):
            return get_developer_api_key_error_response()
        opportunity = db.Opportunity.create(session, request)
        if not isinstance(opportunity, db.Opportunity):
            session.rollback()
            return JSONResponse(fmt.CreateOpportunityFormatter.format_db_errors([opportunity]), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/private/opportunity', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.CreateOpportunityFormatter.format_serializer_errors)
)

def get_opportunity_by_id(session: Session, opportunity_id: ser.ID) -> db.Opportunity | None:
    """Get opportunity by id. Returns None if opportunity with provided id doesn't exist."""

    return session.get(db.Opportunity, opportunity_id)

@app.post('/api/private/opportunity/tags')
def add_opportunity_tags(request: ser.Opportunity.AddTags) -> JSONResponse:
    class ErrorCode(IntEnum):
        INVALID_OPPORTUNITY_ID = 200

    with db.Session.begin() as session:
        api_key = get_developer_api_key(session, request.api_key)
        if not isinstance(api_key, db.DeveloperAPIKey):
            return get_developer_api_key_error_response()
        opportunity = get_opportunity_by_id(session, request.opportunity_id)
        if opportunity is None:
            return JSONResponse(fmt.GetOpportunityByIDFormatter.get_db_error(code=ErrorCode.INVALID_OPPORTUNITY_ID),
                                status_code=422)
        errors = opportunity.add_tags(session, request)
        if errors is not None:
            session.rollback()
            return JSONResponse(fmt.AddOpportunityTagFormatter.format_db_errors(errors), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/private/opportunity/tags', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.AddOpportunityTagFormatter.format_serializer_errors)
)

@app.post('/api/private/opportunity/geotags')
def add_opportunity_geo_tags(request: ser.Opportunity.AddGeoTags) -> JSONResponse:
    class ErrorCode(IntEnum):
        INVALID_OPPORTUNITY_ID = 200

    with db.Session.begin() as session:
        api_key = get_developer_api_key(session, request.api_key)
        if not isinstance(api_key, db.DeveloperAPIKey):
            return get_developer_api_key_error_response()
        opportunity = get_opportunity_by_id(session, request.opportunity_id)
        if opportunity is None:
            return JSONResponse(fmt.GetOpportunityByIDFormatter.get_db_error(code=ErrorCode.INVALID_OPPORTUNITY_ID),
                                status_code=422)
        errors = opportunity.add_geo_tags(session, request)
        if errors is not None:
            session.rollback()
            return JSONResponse(fmt.AddOpportunityGeoTagFormatter.format_db_errors(errors), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/private/opportunity/geotags', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.AddOpportunityGeoTagFormatter.format_serializer_errors)
)

@app.patch('/api/private/opportunity/description')
def update_opportunity_description(
    query: Annotated[ser.Opportunity.QueryParameters, Query()],
    description: UploadFile,
) -> JSONResponse:
    class ErrorCode(IntEnum):
        INVALID_OPPORTUNITY_ID = 200

    # Temporary solution, FastAPI doesn't support file content type validation
    if description.content_type != 'text/markdown':
        return JSONResponse(fmt.UpdateOpportunityDescriptionFormatter.get_invalid_content_type_error(),
                            status_code=422)
    with db.Session.begin() as session:
        api_key = get_developer_api_key(session, query.api_key)
        if not isinstance(api_key, db.DeveloperAPIKey):
            return get_developer_api_key_error_response()
        opportunity = get_opportunity_by_id(session, query.opportunity_id)
        if opportunity is None:
            return JSONResponse(fmt.GetOpportunityByIDFormatter.get_db_error(code=ErrorCode.INVALID_OPPORTUNITY_ID),
                                status_code=422)
        opportunity.update_description(db.minio_client, db.File(description.file, description.size))
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/private/opportunity/description', 'PATCH',
    handler=default_request_validation_error_handler_factory(fmt.UpdateOpportunityDescriptionFormatter.format_serializer_errors)
)

@app.put('/api/private/opportunity/form/submit')
def update_opportunity_form_submit(
    query: Annotated[ser.Opportunity.QueryParameters, Query()],
    submit: ser.Opportunity.UpdateFormSubmit,
) -> JSONResponse:
    class ErrorCode(IntEnum):
        INVALID_OPPORTUNITY_ID = 200

    with db.Session.begin() as session:
        api_key = get_developer_api_key(session, query.api_key)
        if not isinstance(api_key, db.DeveloperAPIKey):
            return get_developer_api_key_error_response()
        opportunity = get_opportunity_by_id(session, query.opportunity_id)
        if opportunity is None:
            return JSONResponse(fmt.GetOpportunityByIDFormatter.get_db_error(code=ErrorCode.INVALID_OPPORTUNITY_ID),
                                status_code=422)
        ...
    return JSONResponse({})

@app.put('/api/private/opportunity/form/fields')
def update_opportunity_form_fields(
    query: Annotated[ser.Opportunity.QueryParameters, Query()],
    fields: ser.Opportunity.UpdateFormFields,
) -> JSONResponse:
    ...
    return JSONResponse({})


@app.post('/api/private/opportunity-tag')
def create_opportunity_tag(request: ser.OpportunityTag.Create) -> JSONResponse:
    with db.Session.begin() as session:
        api_key = get_developer_api_key(session, request.api_key)
        if not isinstance(api_key, db.DeveloperAPIKey):
            return get_developer_api_key_error_response()
        tag_or_error = db.OpportunityTag.create(session, request)
        if not isinstance(tag_or_error, db.OpportunityTag):
            session.rollback()
            return JSONResponse(fmt.CreateOpportunityTagFormatter.format_db_errors([tag_or_error]), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/private/opportunity-tag', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.CreateOpportunityTagFormatter.format_serializer_errors)
)

@app.post('/api/private/opportunity-geotag')
def create_opportunity_geo_tag(request: ser.OpportunityGeoTag.Create) -> JSONResponse:
    with db.Session.begin() as session:
        api_key = get_developer_api_key(session, request.api_key)
        if not isinstance(api_key, db.DeveloperAPIKey):
            return get_developer_api_key_error_response()
        tag_or_error = db.OpportunityGeoTag.create(session, request)
        if not isinstance(tag_or_error, db.OpportunityGeoTag):
            session.rollback()
            return JSONResponse(fmt.CreateOpportunityGeoTagFormatter.format_db_errors([tag_or_error]), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/private/opportunity-geotag', 'POST',
    handler=default_request_validation_error_handler_factory(
        fmt.CreateOpportunityGeoTagFormatter.format_serializer_errors)
)

# TODO
@app.post('/api/opportunity-card')
def create_opportunity_card(request: ser.OpportunityCard.Create) -> JSONResponse:
    ...
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/opportunity-card', 'POST',
    handler=...
)

# TODO: figure out NoSQL, add error formatter
@app.post('/api/opportunity-response')
def create_opportunity_response(request: ser.OpportunityResponse.Create) -> JSONResponse:
    ...
    return JSONResponse({})
