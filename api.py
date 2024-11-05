from typing import Iterable

from config import *
from fastapi.responses import JSONResponse

import db as db
import serializers.mod as ser
import formatters.mod as fmt


def default_request_validation_error_handler_factory(
        error_formatter: Callable[[Iterable[fmt.base.PydanticError]], fmt.base.Result]
) -> RequestValidationErrorHandler:
    def handler_fn(e: RequestValidationError) -> JSONResponse:
        return JSONResponse(error_formatter(e.errors()), status_code=422)

    return handler_fn


@app.post('/api/user')
def create_user(request: ser.User.Create) -> JSONResponse:
    with db.Session.begin() as session:
        user_or_error = db.User.create(session, request)
        if not isinstance(user_or_error, db.User):
            session.rollback()
            return JSONResponse(fmt.CreateUserFormatter.format_db_errors([user_or_error]), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/user', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.CreateUserFormatter.format_serializer_errors)
)

@app.post('/login')
async def login_submit_handler(request: ser.User.Login) -> JSONResponse:
    with db.Session.begin() as session:
        user_or_none = db.User.login(session, request)
        if user_or_none is None:
            return JSONResponse({}, status_code=401)
        response = JSONResponse({})
        # TODO: add session tokens
        response.set_cookie('user_id', str(user_or_none.id))
    return response

register_request_validation_error_handler(
    '/login', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.LoginFormatter.format_serializer_errors)
)

@app.patch('/api/user/info')
def update_user_info(request: ser.UserInfo.Update) -> JSONResponse:
    with db.Session.begin() as session:
        none_or_error = db.UserInfo.update(session, request)
        if none_or_error is not None:
            session.rollback()
            return JSONResponse(fmt.UpdateUserInfoFormatter.format_db_errors([none_or_error]), status_code=422)
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

# TODO: figure out S3
@app.patch('/api/user/avatar')
def update_user_avatar(request: ser.UserInfo.UpdateAvatar) -> JSONResponse:
    ...
    return JSONResponse({})

# TODO: figure out S3
@app.post('/api/user/cv')
def add_user_cv(request: ser.UserInfo.UpdateAvatar) -> JSONResponse:
    ...
    return JSONResponse({})

@app.delete('/api/user/cv')
def delete_user_cv(request: ser.CV.Delete) -> JSONResponse:
    with db.Session.begin() as session:
        none_or_error = db.CV.delete(session, request)
        if none_or_error is not None:
            session.rollback()
            return JSONResponse(fmt.DeleteUserCVFormatter.format_db_errors([none_or_error]), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/user/cv', 'DELETE',
    handler=default_request_validation_error_handler_factory(fmt.DeleteUserCVFormatter.format_serializer_errors)
)

@app.post('/api/opportunity-provider')
def create_opportunity_provider(request: ser.OpportunityProvider.Create) -> JSONResponse:
    with db.Session.begin() as session:
        _ = db.OpportunityProvider.create(session, request)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/opportunity-provider', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.CreateProviderFormatter.format_serializer_errors)
)

@app.post('/api/opportunity')
def create_opportunity(request: ser.Opportunity.Create) -> JSONResponse:
    with db.Session.begin() as session:
        opp_or_error = db.Opportunity.create(session, request)
        if not isinstance(opp_or_error, db.Opportunity):
            session.rollback()
            return JSONResponse(fmt.CreateOpportunityFormatter.format_db_errors([opp_or_error]), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/opportunity', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.CreateOpportunityFormatter.format_serializer_errors)
)

@app.post('/api/opportunity/tags')
def add_opportunity_tags(request: ser.Opportunity.AddTags) -> JSONResponse:
    with db.Session.begin() as session:
        none_or_errors = db.Opportunity.add_tags(session, request)
        if none_or_errors is not None:
            session.rollback()
            return JSONResponse(fmt.AddOpportunityTagFormatter.format_db_errors(none_or_errors), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/opportunity/tags', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.AddOpportunityTagFormatter.format_serializer_errors)
)

# TODO: add error formatter
@app.post('/api/opportunity/geotags')
def add_opportunity_geo_tags(request: ser.Opportunity.AddGeoTags) -> JSONResponse:
    ...
    return JSONResponse({})

@app.post('/api/opportunity-tag')
def create_opportunity_tag(request: ser.OpportunityTag.Create) -> JSONResponse:
    with db.Session.begin() as session:
        tag_or_error = db.OpportunityTag.create(session, request)
        if not isinstance(tag_or_error, db.OpportunityTag):
            session.rollback()
            return JSONResponse(fmt.CreateOpportunityTagFormatter.format_db_errors([tag_or_error]), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/opportunity-tag', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.CreateOpportunityTagFormatter.format_serializer_errors)
)

@app.post('/api/opportunity-geotag')
def create_opportunity_geo_tag(request: ser.OpportunityGeoTag.Create) -> JSONResponse:
    with db.Session.begin() as session:
        tag_or_error = db.OpportunityGeoTag.create(session, request)
        if not isinstance(tag_or_error, db.OpportunityGeoTag):
            session.rollback()
            return JSONResponse(fmt.CreateOpportunityGeoTagFormatter.format_db_errors([tag_or_error]), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/opportunity-geotag', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.CreateOpportunityGeoTagFormatter.format_serializer_errors)
)

@app.post('/api/opportunity-card')
def create_opportunity_card(request: ser.OpportunityCard.Create) -> JSONResponse:
    with db.Session.begin() as session:
        card_or_error = db.OpportunityCard.create(session, request)
        if not isinstance(card_or_error, db.OpportunityCard):
            session.rollback()
            return JSONResponse(fmt.CreateOpportunityCardFormatter.format_db_errors([card_or_error]), status_code=422)
    return JSONResponse({})

register_request_validation_error_handler(
    '/api/opportunity-card', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.CreateOpportunityCardFormatter.format_serializer_errors)
)

# TODO: figure out NoSQL, add error formatter
@app.post('/api/opportunity-response')
def create_opportunity_response(request: ser.OpportunityResponse.Create) -> JSONResponse:
    ...
    return JSONResponse({})
