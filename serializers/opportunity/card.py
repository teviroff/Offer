from typing import Annotated
from pydantic import BaseModel, Field

class Create(BaseModel):
    model_config = { 'extra': 'ignore' }

    opportunity_id: Annotated[int, Field(ge=1, strict=True)]
    title: Annotated[str, Field(max_length=30)]
    sub_title: Annotated[Annotated[str, Field(max_length=30)] | None,
                         Field(default=None)]
