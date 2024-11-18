from pydantic import UUID4

from serializers.base import *


class Add(BaseModel):
    model_config = {'extra': 'ignore'}

    name: Annotated[str, Field(max_length=50)]


class Delete(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    cv_id: ID
