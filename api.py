from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

import db as db
import serializers.mod as ser
import formatters.mod as fmt

app = FastAPI()

import logging
import os

LOG_FOLDER = datetime.now().strftime('%d.%m.%Y')
LOG_FILENAME = f'{datetime.now().timestamp()}'

os.makedirs(f'logs/{LOG_FOLDER}', exist_ok=True)
logging.basicConfig(
    filename=f'logs/{LOG_FOLDER}/{LOG_FILENAME}.log',
    format='[%(levelname)s @ %(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)


url_to_error_formatter = {
    # API
    ('/api/user', 'POST'): fmt.CreateUserFormatter,
    ('/api/user/info', 'PATCH'): fmt.UpdateUserInfoFormatter,
    ('/api/user/cv', 'DELETE'): fmt.DeleteUserCVFormatter,
    ('/api/opportunity-provider', 'POST'): fmt.CreateProviderFormatter,
    ('/api/opportunity', 'POST'): fmt.CreateOpportunityFormatter,
    ('/api/opportunity/tags', 'POST'): fmt.AddOpportunityTagFormatter,
    ('/api/opportunity-tag', 'POST'): fmt.CreateOpportunityTagFormatter,
    ('/api/opportunity-geotag', 'POST'): fmt.CreateOpportunityGeoTagFormatter,
    ('/api/opportunity-card', 'POST'): fmt.CreateOpportunityCardFormatter,
    # UI helpers
    ('/login', 'POST'): fmt.LoginFormatter,
}

@app.exception_handler(RequestValidationError)
def validation_error_handler(
    request: Request,
    e: RequestValidationError
) -> JSONResponse:
    if (request.url.path, request.method) in url_to_error_formatter:
        return JSONResponse(
            url_to_error_formatter[(request.url.path, request.method)].format_serializer_errors(e.errors()),
            status_code=422,
        )
    print(e.errors())
    return JSONResponse({}, status_code=500)


@app.post('/api/user')
def create_user(request: ser.User.Create) -> JSONResponse:
    with db.Session.begin() as session:
        user_or_error = db.User.create(session, request)
        if not isinstance(user_or_error, db.User):
            session.rollback()
            return JSONResponse(fmt.CreateUserFormatter.format_db_errors([user_or_error]), status_code=422)
    return JSONResponse({})

@app.post('/login')
async def login_submit_handler(request: ser.User.Login) -> JSONResponse:
    with db.Session.begin() as session:
        user_or_none = db.User.login(session, request)
        if user_or_none is None:
            return JSONResponse({}, status_code=401)
        response = JSONResponse({})
        response.set_cookie('user_id', str(user_or_none.id))
    return response

@app.patch('/api/user/info')
def update_user_info(request: ser.UserInfo.Update) -> JSONResponse:
    with db.Session.begin() as session:
        none_or_error = db.UserInfo.update(session, request)
        if none_or_error is not None:
            session.rollback()
            return JSONResponse(fmt.UpdateUserInfoFormatter.format_db_errors([none_or_error]), status_code=422)
    return JSONResponse({})

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

@app.post('/api/opportunity-provider')
def create_opportunity_provider(request: ser.OpportunityProvider.Create) -> JSONResponse:
    with db.Session.begin() as session:
        _ = db.OpportunityProvider.create(session, request)
    return JSONResponse({})

@app.post('/api/opportunity')
def create_opportunity(request: ser.Opportunity.Create) -> JSONResponse:
    with db.Session.begin() as session:
        opp_or_error = db.Opportunity.create(session, request)
        if not isinstance(opp_or_error, db.Opportunity):
            session.rollback()
            return JSONResponse(fmt.CreateOpportunityFormatter.format_db_errors([opp_or_error]), status_code=422)
    return JSONResponse({})

@app.post('/api/opportunity/tags')
def add_opportunity_tags(request: ser.Opportunity.AddTags) -> JSONResponse:
    with db.Session.begin() as session:
        none_or_errors = db.Opportunity.add_tags(session, request)
        if none_or_errors is not None:
            session.rollback()
            return JSONResponse(fmt.AddOpportunityTagFormatter.format_db_errors(none_or_errors), status_code=422)
    return JSONResponse({})

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

@app.post('/api/opportunity-geotag')
def create_opportunity_geo_tag(request: ser.OpportunityGeoTag.Create) -> JSONResponse:
    with db.Session.begin() as session:
        tag_or_error = db.OpportunityGeoTag.create(session, request)
        if not isinstance(tag_or_error, db.OpportunityGeoTag):
            session.rollback()
            return JSONResponse(fmt.CreateOpportunityGeoTagFormatter.format_db_errors([tag_or_error]), status_code=422)
    return JSONResponse({})

@app.post('/api/opportunity-card')
def create_opportunity_card(request: ser.OpportunityCard.Create) -> JSONResponse:
    with db.Session.begin() as session:
        card_or_error = db.OpportunityCard.create(session, request)
        if not isinstance(card_or_error, db.OpportunityCard):
            session.rollback()
            return JSONResponse(fmt.CreateOpportunityCardFormatter.format_db_errors([card_or_error]), status_code=422)
    return JSONResponse({})

# TODO: figure out NoSQL, add error formatter
@app.post('/api/opportunity-response')
def create_opportunity_response(request: ser.OpportunityResponse.Create) -> JSONResponse:
    ...
    return JSONResponse({})
