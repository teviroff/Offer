from serializers.base import *

class Create(BaseModel):
    ...

class Delete(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    cv_id: ID
