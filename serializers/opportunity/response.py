from typing import Annotated
from pydantic import BaseModel, Field

class Create(BaseModel):
    model_config = { 'extra': 'ignore' }

    user_id: Annotated[int, Field(ge=1, strict=True)]
    opportunity_id: Annotated[int, Field(ge=1, strict=True)]
