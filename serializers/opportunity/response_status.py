from serializers.base import *
from datetime import datetime


class Create(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    response_id: ID
    status: Annotated[str, Field(max_length=50)]
    description: Annotated[str, Field(max_length=200)]
    timestamp: Annotated[datetime, Field(default_factory=datetime.now)]
