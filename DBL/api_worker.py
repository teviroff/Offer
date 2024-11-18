import requests
from DBL.config import *
from DBL.forms import convert_field_for_db


def create_provider(provider_name: str) -> int:
    json = {
        "name": provider_name,
        "api_key": "personal-9a9bdc8808d2573f2ceb72ff106027d8872273dc2df53488a5cc6b098dd90bfe"
    }
    response = requests.post('/api/private/opportunity-provider', json=json)
    if response:
        return response.json()['id']
    return -1



def create_opportunity(opportunity):
    provider_id = create_provider(opportunity['provider'])  # TODO: provider identify?
    if provider_id < 0:
        dbl_logger.error(f'Can not create provider for opportunity {opportunity["name"]}')
        return -1

    json = {
        "name": opportunity['name'],
        "link": opportunity['link'],
        "provider_id": provider_id,
        "api_key": "personal-ce3ef515c792b507eb32ad6d251015a8df63e5337f86f67db990326508b1bdb1"
    }
    if 'form' in opportunity:
        json['fields'] = {
            "form_link": opportunity['form_link'],
            "fields": [convert_field_for_db(name, field) for name, field in opportunity['form'].items()]
        }
    # Send
    response = requests.post('/api/private/opportunity', json=json)

    if not response:
        dbl_logger.error(f'Can not create opportunity "{opportunity["name"]}" record')
        return -1
    return response.json()['id']


def load_md_desc(opp_id, fname):
    # TODO: update desc MD!
    pass
