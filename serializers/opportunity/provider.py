from serializers.base import *


class CreateFields(BaseModel):
    model_config = {'extra': 'ignore'}

    name: Annotated[str, Field(min_length=4, max_length=50)]

class Create(CreateFields):
    api_key: API_KEY


class UpdateLogo(BaseModel):
    ...
