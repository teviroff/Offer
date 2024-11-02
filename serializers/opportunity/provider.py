from typing import Annotated
from pydantic import BaseModel, Field

class Create(BaseModel):
    model_config = { 'extra': 'ignore' }

    name: Annotated[str, Field(min_length=4, max_length=50)]

class UpdateLogo(BaseModel):
    ...
