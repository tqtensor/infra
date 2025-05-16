import pulumi_azure_native as az
from pulumi import Output

from resources.resource_group import victor_resource_group
from resources.utils import get_options

OPTS = get_options(
    profile="quickqr", region="sweden", type="resource", provider="az", protect=False
)


openai_account = az.cognitiveservices.Account(
    "openai_account",
    account_name="victor-openai",
    kind="OpenAI",
    resource_group_name=victor_resource_group.name,
    sku=az.cognitiveservices.SkuArgs(name="S0"),
    opts=OPTS,
)

openai_account_details = az.cognitiveservices.get_account_output(
    account_name=openai_account.name,
    resource_group_name=victor_resource_group.name,
)

openai_keys = Output.all(openai_account.name, victor_resource_group.name).apply(
    lambda args: az.cognitiveservices.list_account_keys(
        resource_group_name=args[1], account_name=args[0]
    )
)

gpt_o4_mini_deployment = az.cognitiveservices.Deployment(
    "gpt_o4_mini_deployment",
    account_name=openai_account.name,
    deployment_name="o4-mini",
    properties={
        "model": {
            "format": "OpenAI",
            "name": "o4-mini",
            "version": "2025-04-16",
        },
        "version_upgrade_option": az.cognitiveservices.DeploymentModelVersionUpgradeOption.ONCE_NEW_DEFAULT_VERSION_AVAILABLE,
    },
    resource_group_name=victor_resource_group.name,
    sku={
        "capacity": 100,
        "name": "GlobalStandard",
    },
    opts=OPTS,
)

gpt_41 = az.cognitiveservices.Deployment(
    "gpt_41",
    account_name=openai_account.name,
    deployment_name="gpt-4.1",
    properties={
        "model": {
            "format": "OpenAI",
            "name": "gpt-4.1",
            "version": "2025-04-14",
        },
        "version_upgrade_option": az.cognitiveservices.DeploymentModelVersionUpgradeOption.ONCE_NEW_DEFAULT_VERSION_AVAILABLE,
    },
    resource_group_name=victor_resource_group.name,
    sku={
        "capacity": 100,
        "name": "GlobalStandard",
    },
    opts=OPTS,
)
