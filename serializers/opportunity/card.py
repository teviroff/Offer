from serializers.base import *


class Create(BaseModel):
    model_config = {'extra': 'ignore'}

    api_key: API_KEY
    opportunity_id: ID
    title: Annotated[str, Field(min_length=1, max_length=30)]
    sub_title: Annotated[Annotated[str, Field(min_length=1, max_length=30)] | None, Field(default=None)]
