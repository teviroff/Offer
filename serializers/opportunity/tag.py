from serializers.base import *


class Create(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    name: Annotated[str, Field(min_length=1, max_length=50)]
