# import logging, os
# from datetime import datetime

# LOG_FOLDER = datetime.now().strftime('%d.%m.%Y')
# LOG_FILENAME = f'{datetime.now().timestamp()}'
#
# os.makedirs(f'logs/{LOG_FOLDER}', exist_ok=True)
# logging.basicConfig(
#     filename=f'logs/{LOG_FOLDER}/{LOG_FILENAME}.log',
#     format='[%(levelname)s @ %(asctime)s] %(message)s',
#     datefmt='%H:%M:%S',
#     level=logging.DEBUG
# )

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='templates')

print(templates.get_template('info/cv.html').render())
