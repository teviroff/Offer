import api
import ui
from config import app, HOST, PORT
from uvicorn import run

if __name__ == '__main__':
    run('config:app', host=HOST, port=PORT)
