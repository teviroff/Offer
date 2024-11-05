from typing import Annotated

from app import *
from uvicorn import run
from fastapi import Path
from fastapi.responses import RedirectResponse


somedata = {
    'name': 'Junior C#',
    'provider': {'name': 'Yandex',},
    'tags': [{'name': 'C#'}, {'name': 'Backend'}],
    'geo_tags': [{'city_name': 'Moscow'}, {'city_name': 'Peter'}],
    'description': 'C# ASP .NET'
}

@app.get('/opportunity/{opportunity_id}')
def opportunity(request: Request, opportunity_id: Annotated[int, Path()]):
    ...
    somedata['request'] = request
    return templates.TemplateResponse('opportunity.html', context=somedata)

carddata = {
    'title': 'C# Junior Desktop',
    'sub_title': 'MaUI .NET',
    'provider': {
        'name': 'MICROSOFT'
    },
    'tags': [{'name': 'C#'}, {'name': 'MaUI'}],
    'geo_tags': [{'city_name': 'Moscow'}, {'city_name': 'Peter'}]
}
@app.get("/card")
def card(request: Request):
    carddata['request'] = request
    return templates.TemplateResponse(name='card.html', context=carddata)

@app.get('/')
def root(request: Request):
    user_id = request.cookies.get('user_id')
    if user_id is not None:
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


if __name__ == '__main__':
    run('ui:app')
