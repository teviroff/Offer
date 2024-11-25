from serializers.base import *


class Id(BaseModel):
    model_config = {'extra': 'ignore'}

    cv_id: ID

class Name(BaseModel):
    model_config = {'extra': 'ignore'}

    name: Annotated[str, Field(min_length=1, max_length=50)]

class Rename(Id, Name):
    pass
