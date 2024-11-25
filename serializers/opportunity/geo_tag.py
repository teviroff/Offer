from serializers.base import *


class CreateFields(BaseModel):
    model_config = {'extra': 'ignore'}

    city_id: ID

class Create(CreateFields):
    api_key: API_KEY
