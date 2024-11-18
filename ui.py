from typing import Annotated
from enum import IntEnum
from ipaddress import IPv4Address

from pydantic import ValidationError
from fastapi import UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api import default_request_validation_error_handler_factory
from config import *
import db
import serializers.mod as ser
import formatters.mod as fmt
import middleware as mw


def get_api_key_model(request: Request) -> ser.APIKey | ValidationError:
    """Extract 'api_key' from request cookies and validate it."""

    cookie = request.cookies.get('api_key')
    assert cookie is not None
    try:
        return ser.APIKey(key=cookie)
    except ValidationError as error:
        return error

def get_optional_api_key_model(request: Request) -> ser.APIKey | None | ValidationError:
    """Same as 'get_api_key_model', but allows key to be missing."""

    cookie = request.cookies.get('api_key')
    if cookie is None:
        return
    try:
        return ser.APIKey(key=cookie)
    except ValidationError as error:
        return error

def get_api_key_error_json(error: ValidationError) -> JSONResponse:
    """Returns JSON response with errors."""

    return JSONResponse(fmt.GetAPIKeyFormatter.format_serializer_errors(error.errors()), status_code=422)

def get_api_key_error_redirect(error: ValidationError) -> RedirectResponse:
    """Redirects to '/cookie/corrupted' or '/login' depending on error code."""

    errors = fmt.GetAPIKeyFormatter.format_serializer_errors(error.errors())
    if errors['api_key'][0]['type'] == fmt.FieldErrorCode.MISSING:
        return RedirectResponse('/login')
    return RedirectResponse('/cookie')

class GetPersonalAPIKeyErrorCode(IntEnum):
    DOESNT_EXIST = 0
    NOT_PERSONAL = 1
    WRONG_CLIENT = 2

def get_personal_api_key(request: Request, session: Session, key: ser.APIKey) \
        -> db.PersonalAPIKey | GetPersonalAPIKeyErrorCode:
    """Asserts that given API key exists and is personal."""

    api_key = db.APIKey.get(session, key)
    if api_key is None:
        return GetPersonalAPIKeyErrorCode.DOESNT_EXIST
    if not isinstance(api_key, db.PersonalAPIKey):
        return GetPersonalAPIKeyErrorCode.NOT_PERSONAL
    if str(api_key.ip) != request.client.host or api_key.port != request.client.port:
        api_key.expire(session)
        return GetPersonalAPIKeyErrorCode.WRONG_CLIENT
    return api_key

def get_personal_api_key_error_json() -> JSONResponse:
    """Return JSON response with errors."""

    return JSONResponse(fmt.GetAPIKeyFormatter.get_db_error(), status_code=422)

def get_personal_api_key_error_redirect(error_code: GetPersonalAPIKeyErrorCode) -> RedirectResponse:
    """Redirects to '/cookie/expired' or '/cookie/corrupted' depending on error code."""

    redirect_url = None
    match error_code:
        case GetPersonalAPIKeyErrorCode.DOESNT_EXIST:
            redirect_url = '/cookie/expired'
        case GetPersonalAPIKeyErrorCode.NOT_PERSONAL | GetPersonalAPIKeyErrorCode.WRONG_CLIENT:
            redirect_url = '/cookie/corrupted'
    assert redirect_url is not None
    return RedirectResponse(redirect_url)


@app.get('/cookie/corrupted')
def cookie_corrupted(request: Request):
    response = templates.TemplateResponse(request, 'cookie_corrupted.html')
    response.delete_cookie('api_key')
    return response

@app.get('/cookie/expired')
def cookie_expired(request: Request):
    response = templates.TemplateResponse(request, 'cookie_expired.html')
    response.delete_cookie('api_key')
    return response


@app.get('/')
def root(request: Request):
    api_key = get_optional_api_key_model(request)
    if api_key is None:
        return templates.TemplateResponse(request, 'landing.html')
    if not isinstance(api_key, ser.APIKey):
        return get_api_key_error_redirect(api_key)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return get_personal_api_key_error_redirect(personal_api_key)
        return templates.TemplateResponse(request, 'main.html',
                                          context={'fullname': personal_api_key.user.user_info.fullname})

@app.get('/register')
def register(request: Request):
    if request.cookies.get('api_key') is not None:
        return RedirectResponse('/')
    return templates.TemplateResponse(request, 'register.html')

# TODO: add redirect get parameter support
@app.get('/login')
def login(request: Request):
    if request.cookies.get('api_key') is not None:
        return RedirectResponse('/')
    return templates.TemplateResponse(request, 'login.html')

@app.post('/login')
async def login_handler(request: Request, fields: ser.User.LoginFields) -> JSONResponse:
    # 'request.client' may be None by specification, but this only occurs when using FastAPI TestClient,
    # which is not currently used. If this changes in the future, do not forget to handle this case
    assert request.client is not None
    ip, port = (IPv4Address(request.client.host), request.client.port)
    with db.Session.begin() as session:
        login_request = ser.User.Login.model_construct(**fields.model_dump(),
                                                       ip=ip, port=port)
        api_key = mw.authorize_user(session, login_request)
        if api_key is None:
            return JSONResponse({}, status_code=401)
        response = JSONResponse({})
        response.set_cookie('api_key', str(api_key), expires=api_key.expiry_date)
    return response

register_request_validation_error_handler(
    '/login', 'POST',
    handler=default_request_validation_error_handler_factory(fmt.LoginFormatter.format_serializer_errors),
)

@app.post('/logout')
def logout_handler(request: Request) -> JSONResponse:
    api_key = get_optional_api_key_model(request)
    if not isinstance(api_key, ser.APIKey):
        response = JSONResponse({})
        if api_key is not None:
            response.delete_cookie('api_key')
        return response
    response = JSONResponse({})
    response.delete_cookie('api_key')
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return response
        personal_api_key.expire(session)
    return response


@app.get('/me')
def user_info(request: Request):
    api_key = get_api_key_model(request)
    if not isinstance(api_key, ser.APIKey):
        return get_api_key_error_redirect(api_key)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return get_personal_api_key_error_redirect(personal_api_key)
        info = personal_api_key.user.get_info()
    return templates.TemplateResponse(request, 'info.html', context=info)

@app.patch('/me')
async def user_info_update_handler(request: Request) -> JSONResponse:
    ...

# @app.patch('/info')
# async def update_user_info(request: Request, fields: ser.UserInfo.UpdateFields) -> JSONResponse:
#     api_key = get_api_key_json(request)
#     if not isinstance(api_key, ser.APIKey):
#         return api_key
#     with db.Session.begin() as session:
#         personal_api_key = get_personal_api_key_json(session, api_key)
#         if not isinstance(personal_api_key, db.PersonalAPIKey):
#             return personal_api_key
#         personal_api_key.user.user_info.update(session, fields)
#     return JSONResponse({})
#
# @app.post('/info/cv')
# async def add_user_cv(request: Request, cv: UploadFile) -> JSONResponse:
#     api_key = get_api_key_json(request)
#     if not isinstance(api_key, ser.APIKey):
#         return api_key
#     with db.Session.begin() as session:
#         personal_api_key = get_personal_api_key_json(session, api_key)
#         if not isinstance(personal_api_key, db.PersonalAPIKey):
#             return personal_api_key
#         filename = db.CV.generate_filename(session)
#         db.minio_client.put_object('user-cv', f'{filename}.pdf', cv.file, cv.size)
#         db.CV.add(session, personal_api_key.user, ser.CV.AddFields.model_construct(filename=filename))
#     return JSONResponse({})
#
# @app.delete('/info/cv')
# async def delete_user_cv(request: Request, fields: ser.CV.DeleteFields) -> JSONResponse:
#     api_key = get_api_key_json(request)
#     if not isinstance(api_key, ser.APIKey):
#         return api_key
#     with db.Session.begin() as session:
#         personal_api_key = get_personal_api_key_json(session, api_key)
#         if not isinstance(personal_api_key, db.PersonalAPIKey):
#             return personal_api_key
#         error = db.CV.delete(session, minio_client, personal_api_key, fields, check_permissions=False)
#         if error is not None:
#             session.rollback()
#             return JSONResponse(fmt.DeleteUserCVFormatter.format_db_errors([error]), status_code=422)
#     return JSONResponse({})

# @app.get('/opportunity/{opportunity_id}')
# def opportunity(request: Request, opportunity_id: Annotated[int, Path()]):
#     if request.cookies.get('user_id') is None:
#         return RedirectResponse('/login')
#     with db.Session.begin() as session:
#         dict_or_none = db.Opportunity.get_dict(session, opportunity_id)
#         if dict_or_none is None:
#             return page_not_found_response(request)
#     return templates.TemplateResponse(request, 'opportunity.html', context=dict_or_none)

# carddata = {
#     'title': 'C# Junior Desktop',
#     'sub_title': 'MaUI .NET',
#     'provider': {
#         'name': 'MICROSOFT'
#     },
#     'tags': [{'name': 'C#'}, {'name': 'MaUI'}],
#     'geo_tags': [{'city_name': 'Moscow'}, {'city_name': 'Peter'}]
# }
# @app.get('/card')
# def card(request: Request):
#     carddata['request'] = request
#     return templates.TemplateResponse(name='card.html', context=carddata)

# @app.post('/getcities')
# async def GetCities(request: Request):
#     country = (await request.json()).get('country')
#
#     print(countries[country])
#     return JSONResponse(content=countries[country], status_code=200)
#
