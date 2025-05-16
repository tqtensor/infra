import pulumi_azure_native as az

from resources.providers.az import az_quickqr_sweden
from resources.utils import get_options

OPTS = get_options(profile="quickqr", region="sweden", type="resource", provider="az")


victor_resource_group = az.resources.ResourceGroup(
    "victor_resource_group",
    resource_group_name="victor-resource-group",
    location=az_quickqr_sweden.get_provider(module_member="location"),
    opts=OPTS,
)
