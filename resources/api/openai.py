import pulumi_azure_native as az
from pulumi import Output

from resources.providers.az import az_quickqr_sweden
from resources.utils import get_options

OPTS = get_options(profile="quickqr", region="sweden", type="resource", provider="az")


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

openai_account_details = az.cognitiveservices.get_account_output(
    account_name=openai_account.name,
    resource_group_name=openai_resource_group.name,
)

openai_keys = Output.all(openai_account.name, openai_resource_group.name).apply(
    lambda args: az.cognitiveservices.list_account_keys(
        resource_group_name=args[1], account_name=args[0]
    )
)

gpt_4o_deployment = az.cognitiveservices.Deployment(
    "gpt_4o_deployment",
    account_name=openai_account.name,
    deployment_name="gpt-4o",
    properties={
        "model": {
            "format": "OpenAI",
            "name": "gpt-4o",
            "version": "2024-11-20",
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

gpt_o1_deployment = az.cognitiveservices.Deployment(
    "gpt_o1_deployment",
    account_name=openai_account.name,
    deployment_name="o1",
    properties={
        "model": {
            "format": "OpenAI",
            "name": "o1",
            "version": "2024-12-17",
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

gpt_45_preview_deployment = az.cognitiveservices.Deployment(
    "gpt_45_preview_deployment",
    account_name=openai_account.name,
    deployment_name="gpt-4.5-preview",
    properties={
        "model": {
            "format": "OpenAI",
            "name": "gpt-4.5-preview",
            "version": "2025-02-27",
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
