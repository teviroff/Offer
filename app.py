from typing import Annotated
from datetime import datetime

from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.templating import Jinja2Templates
import uvicorn

import db as db
import serializers.mod as ser
import formatters.mod as fmt

app = FastAPI()
templates = Jinja2Templates(directory='templates')

import logging, os

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
    ('/api/user', 'POST'): fmt.CreateUser.POSTFormatter,
}

@app.exception_handler(RequestValidationError)
def validation_error_handler(
    request: Request,
    e: RequestValidationError
) -> JSONResponse:
    if (request.url.path, request.method) in url_to_error_formatter:
        return JSONResponse(
            content=url_to_error_formatter[(request.url.path, request.method)]
                        .format_serializer_errors(e.errors()),
            status_code=422,
        )
    print(e.errors())
    return JSONResponse(content={}, status_code=500)

@app.post('/api/user')
def create_user(
    api_key: Annotated[str | None, Query()] = None,
    request: ser.User.Create = ...,
) -> JSONResponse:
    with db.Session.begin() as session:
        user_or_error = db.User.create(session, request)
        if not isinstance(user_or_error, db.User):
            session.rollback()
            return JSONResponse(
                content=fmt.CreateUser.POSTFormatter \
                    .format_db_error(user_or_error),
                status_code=422,
            )
    return JSONResponse({})

# TODO: add error formatter
@app.patch('/api/user/info')
def update_user_info(
    api_key: Annotated[str | None, Query()] = None,
    request: ser.UserInfo.Update = ...,
) -> JSONResponse:
    with db.Session.begin() as session:
        none_or_error = db.UserInfo.update(session, request)
        if none_or_error is not None:
            session.rollback()
            return JSONResponse(
                content=...,
                status_code=422,
            )
    return JSONResponse({})

# TODO: figure out S3, add error formatter
@app.patch('/api/user/avatar')
def update_user_avatar(
    api_key: Annotated[str | None, Query()] = None,
    request: ser.UserInfo.UpdateAvatar = ...,
) -> JSONResponse:
    ...
    return JSONResponse({})

# TODO: add error formatter
@app.post('/api/opprovider')
def create_opportunity_provider(
    api_key: Annotated[str, Query()] = ...,
    request: ser.OpportunityProvider.Create = ...
) -> JSONResponse:
    with db.Session.begin() as session:
        _ = db.OpportunityProvider.create(session, request)
    return JSONResponse({})

# TODO: add error formatter
@app.post('/api/opportunity')
def create_opportunity(
    api_key: Annotated[str, Query()] = ...,
    request: ser.Opportunity.Create = ...
) -> JSONResponse:
    with db.Session.begin() as session:
        opp_or_error = db.Opportunity.create(session, request)
        if not isinstance(opp_or_error, db.Opportunity):
            session.rollback()
            return JSONResponse(
                content=...,
                status_code=422,
            )
    return JSONResponse({})

# TODO: add error formatter
@app.post('/api/opportunity/tags')
def add_opportunity_tags(
    api_key: Annotated[str, Query()] = ...,
    request: ser.Opportunity.AddTags = ...,
) -> JSONResponse:
    ...
    return JSONResponse({})

# TODO: add error formatter
@app.post('/api/opportunity/geotags')
def add_opportunity_geo_tags(
    api_key: Annotated[str, Query()] = ...,
    request: ser.Opportunity.AddGeoTags = ...,
) -> JSONResponse:
    ...
    return JSONResponse({})

# TODO: add error formatter
@app.post('/api/opptag')
def create_opportunity_tag(
    api_key: Annotated[str, Query()] = ...,
    request: ser.OpportunityTag.Create = ...
) -> JSONResponse:
    with db.Session.begin() as session:
        tag_or_error = db.OpportunityTag.create(session, request)
        if not isinstance(tag_or_error, db.OpportunityTag):
            session.rollback()
            return JSONResponse(
                content=...,
                status_code=422,
            )
    return JSONResponse({})

# TODO: add error formatter
@app.post('/api/oppgeotag')
def create_opportunity_geo_tag(
    api_key: Annotated[str, Query()] = ...,
    request: ser.OpportunityGeoTag.Create = ...,
) -> JSONResponse:
    with db.Session.begin() as session:
        tag_or_error = db.OpportunityGeoTag.create(session, request)
        if not isinstance(tag_or_error, db.OpportunityGeoTag):
            session.rollback()
            return JSONResponse(
                content=...,
                status_code=422,
            )
    return JSONResponse({})

# TODO: add error formatter
@app.post('/api/oppcard')
def create_opportunity_card(
    api_key: Annotated[str, Query()] = ...,
    request: ser.OpportunityCard.Create = ...,
) -> JSONResponse:
    ...
    return JSONResponse({})

# TODO: figure out NoSQL, add error formatter
@app.post('/api/oppresponse')
def create_opportunity_response(
    api_key: Annotated[str | None, Query()] = None,
    request: ser.OpportunityResponse.Create = ...,
) -> JSONResponse:
    ...
    return JSONResponse({})

if __name__ == "__main__":
    uvicorn.run("app:app")
