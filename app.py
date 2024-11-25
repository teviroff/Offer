import api
import ui
from config import app
from minio import Minio
from uvicorn import run

import pymongo

if __name__ == '__main__':
    run('config:app')
