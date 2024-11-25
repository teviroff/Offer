from typing import Annotated
from enum import IntEnum
from ipaddress import IPv4Address

from pydantic import ValidationError
from fastapi import UploadFile, Path
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, HTMLResponse

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
    if not LOCAL and (str(api_key.ip) != request.client.host or api_key.port != request.client.port):
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
    handler=default_request_validation_error_handler_factory(fmt.LoginFormatter.format_serializer_errors)
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
    return templates.TemplateResponse(request, 'info/page.html', context=info)

@app.patch('/me')
async def user_info_update_handler(request: Request, fields: ser.UserInfo.UpdateFields) -> JSONResponse:
    api_key = get_api_key_model(request)
    if not isinstance(api_key, ser.APIKey):
        return get_api_key_error_json(api_key)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return get_personal_api_key_error_json()
        personal_api_key.user.user_info.update(session, fields)
    return JSONResponse({})

register_request_validation_error_handler(
    '/me', 'PATCH',
    handler=default_request_validation_error_handler_factory(fmt.UpdateUserInfoFormatter.format_serializer_errors)
)

@app.post('/me/avatar')
async def update_user_avatar(request: Request, avatar: UploadFile) -> JSONResponse:
    api_key = get_api_key_model(request)
    if not isinstance(api_key, ser.APIKey):
        return get_api_key_error_json(api_key)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return get_personal_api_key_error_json()
        personal_api_key.user.user_info.update_avatar(db.minio_client, db.File(stream=avatar.file, size=avatar.size))
    return JSONResponse({})

@app.get('/me/cvs')
async def get_user_cvs(request: Request) -> HTMLResponse:
    api_key = get_api_key_model(request)
    if not isinstance(api_key, ser.APIKey):
        return HTMLResponse(status_code=422)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return HTMLResponse(status_code=422)
        cvs = personal_api_key.user.get_cvs()
    return HTMLResponse('\n'.join([
        templates.get_template('info/cv.html').render(id=cv_id, name=name) for cv_id, name in cvs]))

@app.post('/me/cv')
async def add_cv(request: Request, cv: UploadFile) -> JSONResponse:
    api_key = get_api_key_model(request)
    if not isinstance(api_key, ser.APIKey):
        return get_api_key_error_json(api_key)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return get_personal_api_key_error_json()
        db.CV.add(session, db.minio_client, personal_api_key.user,
                  db.File(stream=cv.file, size=cv.size), ser.CV.Name(name=cv.filename[:50]))
    return JSONResponse({})

def get_cv_by_id(session: Session, cv_id: ser.ID) -> db.CV | None:
    """Get CV by id. Returns None if CV with provided id doesn't exist."""

    return session.get(db.CV, cv_id)

def get_cv_by_id_error(code: int) -> fmt.ErrorTrace:
    """Return dictionary with CV id errors."""

    return fmt.GetCVByIDFormatter.get_db_error(code=code)

def get_cv_by_id_error_response(code: int) -> JSONResponse:
    """Return JSON response with CV id errors."""

    return JSONResponse(get_cv_by_id_error(code), status_code=422)

@app.patch('/me/cv')
async def rename_cv(request: Request, fields: ser.CV.Rename) -> JSONResponse:
    class ErrorCode(IntEnum):
        INVALID_CV_ID = 200

    api_key = get_api_key_model(request)
    if not isinstance(api_key, ser.APIKey):
        return get_api_key_error_json(api_key)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return get_personal_api_key_error_json()
        cv = get_cv_by_id(session, fields.cv_id)
        if cv is None:
            return get_cv_by_id_error_response(ErrorCode.INVALID_CV_ID)
        if cv.user_info.user_id != personal_api_key.user_id:
            return JSONResponse(fmt.DeleteCVFormatter.get_insufficient_permissions_error(), status_code=422)
        cv.rename(fields)
    return JSONResponse({})

register_request_validation_error_handler(
    '/me/cv', 'PATCH',
    handler=default_request_validation_error_handler_factory(fmt.RenameCVFormatter.format_serializer_errors)
)

@app.delete('/me/cv')
async def delete_cv(request: Request, cv_id: ser.CV.Id) -> JSONResponse:
    class ErrorCode(IntEnum):
        INVALID_CV_ID = 200

    api_key = get_api_key_model(request)
    if not isinstance(api_key, ser.APIKey):
        return get_api_key_error_json(api_key)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return get_personal_api_key_error_json()
        cv = get_cv_by_id(session, cv_id.cv_id)
        if cv is None:
            return get_cv_by_id_error_response(ErrorCode.INVALID_CV_ID)
        if cv.user_info.user_id != personal_api_key.user_id:
            return JSONResponse(fmt.DeleteCVFormatter.get_insufficient_permissions_error(), status_code=422)
        cv.delete(session, db.minio_client)
    return JSONResponse({})

register_request_validation_error_handler(
    '/me/cv', 'DELETE',
    handler=default_request_validation_error_handler_factory(fmt.DeleteCVFormatter.format_serializer_errors)
)

def get_opportunity_by_id(session: Session, opportunity_id: ser.ID) -> db.Opportunity | None:
    """Get opportunity by id. Returns None if opportunity with provided id doesn't exist."""

    return session.get(db.Opportunity, opportunity_id)

@app.get('/opportunity/{opportunity_id}')
def opportunity(request: Request, opportunity_id: Annotated[int, Path(ge=1)]):
    api_key = get_optional_api_key_model(request)
    if api_key is None:
        return RedirectResponse('/login')
    if not isinstance(api_key, ser.APIKey):
        return get_api_key_error_redirect(api_key)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return get_personal_api_key_error_redirect(personal_api_key)
        opportunity = get_opportunity_by_id(session, opportunity_id)
        if opportunity is None:
            return page_not_found_response(request)
        context = opportunity.get_dict()
    context['tags'] = [templates.get_template('opportunity/tag.html').render(id=tag_id, name=name)
                       for tag_id, name in context['tags']]
    context['geo_tags'] = [templates.get_template('opportunity/geotag.html').render(id=tag_id, city_name=city_name)
                           for tag_id, city_name in context['geo_tags']]
    return templates.TemplateResponse(request, 'opportunity/page.html', context=context)

@app.get('/opportunity/{opportunity_id}/description')
def get_opportunity_description(request: Request, opportunity_id: Annotated[int, Path(ge=1)]):
    api_key = get_optional_api_key_model(request)
    if not isinstance(api_key, ser.APIKey):
        return page_access_forbidden(request)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return page_access_forbidden(request)
        opportunity = get_opportunity_by_id(session, opportunity_id)
        if opportunity is None:
            return page_not_found_response(request)
        description = opportunity.get_description(db.minio_client)
    return Response(description, media_type='text/markdown')

@app.get('/opportunity/{opportunity_id}/form')
def get_opportunity_form(request: Request, opportunity_id: Annotated[int, Path(ge=1)]):
    api_key = get_optional_api_key_model(request)
    if not isinstance(api_key, ser.APIKey):
        return page_access_forbidden(request)
    with db.Session.begin() as session:
        personal_api_key = get_personal_api_key(request, session, api_key)
        if not isinstance(personal_api_key, db.PersonalAPIKey):
            return page_access_forbidden(request)
        opportunity = get_opportunity_by_id(session, opportunity_id)
        if opportunity is None:
            return page_not_found_response(request)
        if opportunity.fields is None:
            fields = None
        else:
            fields: db.OpportunityFields | None = db.OpportunityFields.objects(id=opportunity.fields).first()
    if fields is None:
        return HTMLResponse()
    content = ''
    field_type_to_template = {
        db.OpportunityFieldType.String: 'opportunity/fields/string.html',
        db.OpportunityFieldType.Regex: 'opportunity/fields/regex.html',
        db.OpportunityFieldType.Choice: 'opportunity/fields/choice.html',
    }
    for field in fields.fields:
        content += templates.get_template(field_type_to_template[field.type]).render(**field.to_dict())
    return HTMLResponse(content)

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
