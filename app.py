import logging
import os
from datetime import datetime

LOG_FOLDER = datetime.now().strftime('%d.%m.%Y')
LOG_FILENAME = f'{datetime.now().timestamp()}'

os.makedirs(f'logs/{LOG_FOLDER}', exist_ok=True)
logging.basicConfig(
    filename=f'logs/{LOG_FOLDER}/{LOG_FILENAME}.log',
    format='[%(levelname)s @ %(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)

logger = logging.getLogger('application')


from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

app = FastAPI()
app.mount('/scripts', StaticFiles(directory='scripts', html=True), name='scripts')

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='templates')


from typing import Callable
from fastapi import Request
from fastapi.responses import Response
from fastapi.exceptions import RequestValidationError

type RequestValidationErrorHandler = Callable[[RequestValidationError], Response]

url_to_request_validation_error_handler: dict[tuple[str, str], RequestValidationErrorHandler] = {}

@app.exception_handler(RequestValidationError)
def request_validation_error_handler(request: Request, e: RequestValidationError) -> Response:
    if (request.url.path, request.method) in url_to_request_validation_error_handler:
        return url_to_request_validation_error_handler[(request.url.path, request.method)](e)
    logger.error(f'Unhandled request validation errors:\n{"\n".join([str(error) for error in e.errors()])}')
    # TODO: maybe sometimes it's not a 404
    return templates.TemplateResponse('error_404.html', status_code=404, context={'request': request})

def register_request_validation_error_handler(
    url: str, method: str, *,
    handler: RequestValidationErrorHandler
) -> None:
    if (url, method.upper()) in url_to_request_validation_error_handler:
        raise ValueError(f'(\'{url}\', {method.upper()}) already have associated request validation error handler')
    url_to_request_validation_error_handler[(url, method.upper())] = handler
