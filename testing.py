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

from serializers.auxillary import RelativeURL

print(RelativeURL(url='/?redirect=%2Fother%2Fpath%2F%3Fzxc=true').unescaped())
