from typing import Any

from serializers.base import *


class CreateFields(BaseModel):
    model_config = {'extra': 'ignore'}

    data: dict[str, Any]

class Create(CreateFields):
    opportunity_id: ID
