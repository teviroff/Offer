def form_type(field: dict) -> dict:
    tp = field['type']
    if tp == 'number':
        return {"type": "regex", "regex": "^[0-9]*$"}  # TODO: number
    if tp == 'email':
        return {"type": "regex", "regex": r"^((?!\.)[\w\-_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$"}
    if tp == 'choice':
        return {"type": "choice", "choices": field['choices']}
    if tp == 'file':
        return {}  # TODO: file
    # text
    return {"type": "string", "max_length": field["max_length"]}


def convert_field_for_db(name, field) -> dict:
    res = {
            'label': field['label'],
            'is_required': field['required']
    }
    res.update(form_type(field))
    return res
