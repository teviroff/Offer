from serializers.base import *
import serializers.auxillary as _


class Update(BaseModel):
    model_config = {'extra': 'ignore'}

    name: Annotated[Annotated[str, Field(max_length=50)] | None, Field(default=None)]
    surname: Annotated[Annotated[str, Field(max_length=50)] | None, Field(default=None)]
    birthday: Annotated[_.Date | None, Field(default=None)]
    city_id: Annotated[ID | None, Field(default=None)]


class UpdatePhoneNumber(BaseModel):
    ...
