import json
from DBL.config import *


def make_json_path(name: str):
    return f'DBL/json/{name}.json'


def load_from_file(name: str):
    try:
        with open(make_json_path(name)) as file:
            data = json.load(file)
    except FileNotFoundError:
        return {'error': f'file {name} not found'}
    except ValueError:
        return {'error': 'can\'t parse json'}
    except Exception as ex:
        return {'error': f'exception: {ex}'}
    return {'json': data}


def remove_dict_keys(dct: dict, keys: list):
    for rm_key in keys:
        del dct[rm_key]


def clear_record_empty_fields(opp_record: dict):
    keys_to_del = []
    for rec_key, rec_value in opp_record.items():
        if not rec_value:  # types in STD: str, dict, list
            keys_to_del += [rec_key]
    # rm empty keys
    remove_dict_keys(opp_record, keys_to_del)


def record_check_by_keys(opp_record: dict, fname, record_index) -> bool:  # True = success
    not_valid_type_mes = lambda k: f'Opportunity #{record_index} in "{fname}" has not valid type of "{k}" field'

    keys_to_del = []
    models = OPPORTUNITY_FILTER_MODEL.copy()
    for key, value in opp_record.items():
        if key not in models:
            keys_to_del += [key]
            continue
        field_model = models.pop(key)
        field_types = set(field_model['types_supported'])
        # Check for types
        if not any((isinstance(value, tp) for tp in field_types)):
            dbl_logger.error(not_valid_type_mes(key))
            return False
        # Str to list convertation
        if {str, list}.issubset(field_types) and isinstance(value, str):
            opp_record[key] = [value]
        # Check list item types
        if '__list_item_type__' in field_model and isinstance(value, list):
            if not all((any((isinstance(i, j) for j in field_model['__list_item_type__'])) for i in value)):
                dbl_logger.error(not_valid_type_mes(key))
                return False
        # Check dict item types
        if '__dict__item__struct__' in field_model and isinstance(value, dict):
            if set(value.keys()) != set(field_model['__dict__item__struct__']):
                dbl_logger.error(not_valid_type_mes(key))
                return False
    # rm empty keys
    remove_dict_keys(opp_record, keys_to_del)
    # Check remaining models
    req_models = [m_nm for m_nm, m_desc in models if m_desc['required']]
    if req_models:
        dbl_logger.error(f'Opportunity #{record_index} in "{fname}" has not required fields: {", ".join(req_models)}')
        return False
    return True


def filter_opportunity_record(opp_record, fname, record_index):
    if not isinstance(opp_record, dict):
        dbl_logger.error(f'Opportunity #{record_index} in "{fname}" is not a dict instance')
    # Clear empty fields
    clear_record_empty_fields(opp_record)
    # KeyWorker
    record_check_by_keys(opp_record, fname, record_index)
    return opp_record


def parse_opportunity_json(fname: str):
    # Load
    json_data = load_from_file(fname)
    if 'error' in json_data:
        dbl_logger.error(f'Can\' parse all file "{fname}". Reason: {json_data["error"]}')
    dbl_logger.log(logging.INFO, f'Loaded opportunity set file: {fname}')
    # Filter
    if not isinstance(json_data.get('json'), list):
        dbl_logger.error(f'Json file "{fname}" is not list instance')
    filtered_opp_list = []
    for ind, opp_record in enumerate(json_data['json']):
        if filter_opportunity_record(opp_record, fname, ind):
            filtered_opp_list.append(opp_record)
    dbl_logger.log(logging.INFO, f'Filtered opportunity set: {fname}')
    return filtered_opp_list
