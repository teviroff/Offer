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

userupdatedata = {
    'user_id': 0,
    'name': 'Max',
    'surname': 'Flugelev',
    'birthday': {
        'day': 5,
        'month': 11,
        'year': 2006
    },
    # 'city_id': 0,
}

countries = {
    'Russia': ['Moscow', 'Peter', 'Novosibirsk', 'Penza'],
    'Spain': ['Madrid', 'Ronaldo', 'Messi']
}


@app.get("/update")
def update(request: Request):
    data = countries.keys()
    birthday = userupdatedata.get('birthday')
    print(birthday)
    date = f'{birthday.get('year'):04}-{birthday.get('month'):02}-{birthday.get('day'):02}'
    print(date)
    context = {'request': request, 'countries': data, 'user': userupdatedata, 'date': date}
    return templates.TemplateResponse(name='userupdate.html', context=context)


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

@app.post('/getcities')
async def GetCities(request: Request):
    country = (await request.json()).get('country')

    print(countries[country])
    return JSONResponse(content=countries[country], status_code=200)

@app.post('/updateuser')
async def UpdateUser(request: Request):
    newuser = await request.json()
    print(newuser)
    return JSONResponse(content=newuser, status_code=200)

if __name__ == '__main__':
    run('ui:app')
