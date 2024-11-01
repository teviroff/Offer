from datetime import datetime

from pydantic import BaseModel, Field

import logging

logger = logging.getLogger('serializers')

class ResponseStatus(BaseModel):
    model_config = { 'extra': 'ignore' }

    response_id: int = Field(ge=1, strict=True)
    status: str = Field(max_length=50)
    description: str = Field(max_length=200)
    timestamp: datetime = Field(default_factory=datetime.now)

class OpportunityResponse(BaseModel):
    user_id: int = Field(ge=1, strict=True)
    opportunity_id: int = Field(ge=1, strict=True)
    # TODO: data
