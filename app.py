from typing import Annotated
from datetime import datetime

from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.templating import Jinja2Templates
import uvicorn

import db
import serializers.module as ser
import formatters.module as errfmt

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
    '/api/user': errfmt.user.User,
    '/api/userinfo': errfmt.user.UserInfo,
}

@app.exception_handler(RequestValidationError)
def validation_error_handler(
    request: Request,
    e: RequestValidationError
) -> JSONResponse:
    if request.url.path in url_to_error_formatter:
        return JSONResponse(
            content=url_to_error_formatter[request.url.path]
                        .format_serializer_errors(e.errors()),
            status_code=422,
        )
    print(e.errors())
    return JSONResponse(content={}, status_code=500)

@app.post('/api/user')
def create_user(
    api_key: Annotated[str | None, Query()] = None,
    credentials: ser.user.UserCredentials = ...,
) -> JSONResponse:
    with db.Session.begin() as session:
        user_or_error = db.User.create(session, credentials)
        if not isinstance(user_or_error, db.User):
            session.rollback()
            return JSONResponse(
                content=errfmt.user.User.format_db_error(user_or_error),
                status_code=422,
            )
    return JSONResponse({})

@app.patch('/api/userinfo')
def update_user_info(
    api_key: Annotated[str | None, Query()] = None,
    info: ser.user.UserInfo = ...,
) -> JSONResponse:
    with db.Session.begin() as session:
        none_or_error = db.UserInfo.update(session, info)
        if none_or_error is not None:
            session.rollback()
            return JSONResponse(
                content=errfmt.user.UserInfo.format_db_error(none_or_error),
                status_code=422,
            )
    return JSONResponse({})

if __name__ == "__main__":
    uvicorn.run("app:app")
