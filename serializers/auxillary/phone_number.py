from pydantic import BaseModel, Field

import logging

logger = logging.getLogger('serializers')

class PhoneNumber(BaseModel):
    model_config = { 'extra': 'ignore' }

    country_id: int = Field(ge=1, strict=True)
    sub_number: str = Field(max_length=12, pattern=r'\d+')
