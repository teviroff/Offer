import formatters.base as base
from formatters.user import (
    CreateUserFormatter, LoginFormatter,
    UpdateUserInfoFormatter, DeleteUserCVFormatter
)
from formatters.opportunity.provider import CreateProviderFormatter
from formatters.opportunity.opportunity import (
    CreateOpportunityFormatter, AddOpportunityTagFormatter,
    GetOpportunityFormatter,
)
from formatters.opportunity.tag import CreateOpportunityTagFormatter
from formatters.opportunity.geotag import CreateOpportunityGeoTagFormatter
from formatters.opportunity.card import CreateOpportunityCardFormatter
