from typing import Annotated
from pydantic import BaseModel, Field

class Create(BaseModel):
    model_config = { 'extra': 'ignore' }

    name: Annotated[str, Field(max_length=50)]
