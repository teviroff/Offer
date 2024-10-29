from fastapi import FastAPI, Request, Form
from starlette.templating import Jinja2Templates
import uvicorn
import db

app = FastAPI()
templates = Jinja2Templates(directory='templates')

@app.get('/')
def main(request: Request):
    return templates.TemplateResponse(request, 'base.html')

@app.post('/postdata')
def postdata(name = Form(), surname = Form()):
    db.create_user(name, surname)
    return {"name":name, "surname": surname}

if __name__ == "__main__":
    uvicorn.run("app:app")
