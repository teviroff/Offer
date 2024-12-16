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

from db import *

with Session.begin() as session:
    yandex_provider = session.get(OpportunityProvider, 1)
    python_tag = session.get(OpportunityTag, 1)
    cpp_tag = session.get(OpportunityTag, 2)
    moscow_geo_tag = session.get(OpportunityGeoTag, 1)
    spb_geo_tag = session.get(OpportunityGeoTag, 2)
    print([opportunity.name for opportunity in
           Opportunity.filter(session, providers=[yandex_provider], tags=[python_tag], geo_tags=[], page=1)])
