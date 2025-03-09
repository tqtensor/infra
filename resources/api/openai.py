import pulumi_azure_native as az

from resources.providers.az import az_quickqr_sweden
from resources.utils import get_options

OPTS = get_options(
    profile="quickqr", region="sweden", type="resource", provider="az", protect=False
)


openai_resource_group = az.resources.ResourceGroup(
    "openai_resource_group",
    resource_group_name="victor-resource",
    location=az_quickqr_sweden.get_provider(module_member="location"),
    opts=OPTS,
)

openai_account = az.cognitiveservices.Account(
    "openai_account",
    account_name="victor-openai",
    kind="OpenAI",
    resource_group_name=openai_resource_group.name,
    sku=az.cognitiveservices.SkuArgs(name="S0"),
    opts=OPTS,
)

gpt_o3_mini_deployment = az.cognitiveservices.Deployment(
    "gpt_o3_mini_deployment",
    account_name=openai_account.name,
    deployment_name="o3-mini",
    properties={
        "model": {
            "format": "OpenAI",
            "name": "o3-mini",
            "version": "2025-01-31",
        },
        "version_upgrade_option": az.cognitiveservices.DeploymentModelVersionUpgradeOption.ONCE_NEW_DEFAULT_VERSION_AVAILABLE,
    },
    resource_group_name=openai_resource_group.name,
    sku={
        "capacity": 100,
        "name": "GlobalStandard",
    },
    opts=OPTS,
)
