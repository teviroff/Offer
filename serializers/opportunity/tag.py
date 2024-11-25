from serializers.base import *


class CreateFields(BaseModel):
    model_config = {'extra': 'ignore'}

    name: Annotated[str, Field(min_length=1, max_length=50)]

class Create(CreateFields):
    api_key: API_KEY
