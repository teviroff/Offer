import json
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

if __name__ == "__main__":
    uvicorn.run("ui:app")