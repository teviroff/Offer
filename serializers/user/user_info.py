from typing import Annotated, Literal
from pydantic import BaseModel, Field

import serializers.auxillary as _

class Update(BaseModel):
    model_config = { 'extra': 'ignore' }

    user_id: Annotated[int, Field(ge=1, strict=True)]
    name: Annotated[Annotated[str, Field(max_length=50)] | None,
                    Field(default=None)]
    surname: Annotated[Annotated[str, Field(max_length=50)] | None,
                       Field(default=None)]
    birthday: Annotated[_.Date | Literal['reset'] | None, Field(default=None)]
    city_id: Annotated[Annotated[int, Field(ge=1)] | Literal['reset'] | None,
                       Field(default=None)]
    phone_number: Annotated[_.PhoneNumber | Literal['reset'] | None,
                            Field(default=None)]

class UpdateAvatar(BaseModel):
    ...
