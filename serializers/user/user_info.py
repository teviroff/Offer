from pydantic import UUID4

from serializers.base import *
import serializers.auxillary as _


class UpdateFields(BaseModel):
    model_config = {'extra': 'ignore'}

    name: Annotated[Annotated[str, Field(max_length=50)] | None, Field(default=None)]
    surname: Annotated[Annotated[str, Field(max_length=50)] | None, Field(default=None)]
    birthday: Annotated[_.Date | None, Field(default=None)]
    city_id: Annotated[ID | None, Field(default=None)]

class Update(UpdateFields):
    api_key: API_KEY
    user_id: ID


class UpdatePhoneNumber(BaseModel):
    ...
