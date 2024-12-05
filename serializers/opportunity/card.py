from serializers.base import *


class Create(BaseModel):
    model_config = {'extra': 'ignore'}

    title: Annotated[str, Field(min_length=1, max_length=30)]
    subtitle: Annotated[Annotated[str, Field(min_length=1, max_length=30)] | None, Field(default=None)]
