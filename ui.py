import json
from http.client import responses
from pydoc import resolve
from urllib import request

import uvicorn

from fastapi import FastAPI, Form
from fastapi.params import Cookie
from fastapi.responses import FileResponse
from pydantic import RedisDsn
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.mount('/scripts', StaticFiles(directory='scripts', html=True), name='scripts')
templates = Jinja2Templates(directory='templates')
@app.get("/")
def root(request: Request):
    email = request.cookies.get('email')
    if email is None:
        return RedirectResponse(url='/login')
    else:
        return templates.TemplateResponse(name='main.html', context={'request': request, 'email': email})

@app.get("/register")
def register():
    return FileResponse("templates/base.html")
@app.get("/login")
def login(request: Request):
    if request.cookies.get('email') is None:
        return FileResponse("templates/login.html")
    return RedirectResponse(url='/')

somedata = {
    'name': 'Junior C#',
    'provider': {'name': 'Yandex',},
    'tags': [{'name': 'C#'}, {'name': 'Backend'}],
    'geo_tags': [{'city_name': 'Moscow'}, {'city_name': 'Peter'}],
    'description': 'C# ASP .NET'
}
@app.get("/opportunity")
def opportunity(request: Request):
    somedata['request'] = request
    return templates.TemplateResponse(name='opportunity.html', context=somedata)

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


d = {
  "email": [
    {
      "type": 102,
      "message": "Not a valid email address"
    }
  ],
  "password": [
    {
      "type": 102,
      "message": "Password must contain at least one lowercase letter, one uppercase letter, one digit and one special character"
    }
  ]
}

@app.post("/register")
async def RegistrationForm(request: Request):
    return JSONResponse(content="", status_code=200)
    # return JSONResponse(content=d, status_code=422)

@app.post("/login")
async def LoginForm(request: Request):
    response = JSONResponse(content="", status_code=200)
    parsedJson = await request.json()
    response.set_cookie(key="email", value=parsedJson.get("email"))
    response.set_cookie(key="password", value=parsedJson.get("password"))
    return response

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

if __name__ == "__main__":
    uvicorn.run("ui:app")