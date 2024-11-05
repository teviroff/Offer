from typing import Annotated

import db
from config import *
from fastapi import Path
from fastapi.responses import RedirectResponse


@app.get('/opportunity/{opportunity_id}')
def opportunity(request: Request, opportunity_id: Annotated[int, Path()]):
    if request.cookies.get('user_id') is None:
        return RedirectResponse('/login')
    with db.Session.begin() as session:
        dict_or_none = db.Opportunity.get_dict(session, opportunity_id)
        if dict_or_none is None:
            return page_not_found_response(request)
    return templates.TemplateResponse(request, 'opportunity.html', context=dict_or_none)

@app.get('/info')
def user_info(request: Request):
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return RedirectResponse('/login')
    user_id = int(user_id)
    with db.Session.begin() as session:
        dict_or_none = db.User.get_info(session, user_id)
        if dict_or_none is None:  # TODO: user has fake/outdated cookies
            return page_not_found_response(request)
    return templates.TemplateResponse(request, 'userupdate.html', context=dict_or_none)

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

@app.get('/')
def root(request: Request):
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return RedirectResponse('/login')
    return templates.TemplateResponse('main.html', context={'request': request, 'user_id': user_id})

@app.get('/register')
def register(request: Request):
    if request.cookies.get('user_id') is not None:
        return RedirectResponse('/')
    return templates.TemplateResponse('register.html', context={'request': request})

@app.get('/login')
def login(request: Request):
    if request.cookies.get('user_id') is not None:
        return RedirectResponse('/')
    return templates.TemplateResponse('login.html', context={'request': request})

# @app.post('/getcities')
# async def GetCities(request: Request):
#     country = (await request.json()).get('country')
#
#     print(countries[country])
#     return JSONResponse(content=countries[country], status_code=200)
#
