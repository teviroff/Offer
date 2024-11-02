from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field

class Create(BaseModel):
    model_config = { 'extra': 'ignore' }

    response_id: Annotated[int, Field(ge=1, strict=True)]
    status: Annotated[str, Field(max_length=50)]
    description: Annotated[str, Field(max_length=200)]
    timestamp: Annotated[datetime, Field(default_factory=datetime.now)]
