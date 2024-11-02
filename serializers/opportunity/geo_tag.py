from typing import Annotated
from pydantic import BaseModel, Field

class Create(BaseModel):
    model_config = { 'extra': 'ignore' }

    city_id: Annotated[int, Field(ge=1, strict=True)]
