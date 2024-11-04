from serializers.base import *


class Create(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    city_id: ID
