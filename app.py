from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory='templates')

@app.get('/')
def main(request: Request):
    return templates.TemplateResponse(request, 'base.html')