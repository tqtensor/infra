import pulumi
import pulumi_azure_native as az
from pulumi import Output

from resources.resource_group import victor_sweden_resource_group
from resources.utils import get_options

OPTS = get_options(
    profile="quickqr", region="sweden", type="resource", provider="az", protect=False
)


openai_account_sweden = az.cognitiveservices.Account(
    "openai_account_sweden",
    account_name="victor-sweden-openai",
    kind="OpenAI",
    resource_group_name=victor_sweden_resource_group.name,
    sku=az.cognitiveservices.SkuArgs(name="S0"),
    properties=az.cognitiveservices.AccountPropertiesArgs(
        public_network_access=az.cognitiveservices.PublicNetworkAccess.ENABLED,
    ),
    opts=OPTS,
)

openai_account_sweden_details = az.cognitiveservices.get_account_output(
    account_name=openai_account_sweden.name,
    resource_group_name=victor_sweden_resource_group.name,
)

openai_keys_sweden = Output.all(
    openai_account_sweden.name, victor_sweden_resource_group.name
).apply(
    lambda args: az.cognitiveservices.list_account_keys(
        resource_group_name=args[1], account_name=args[0]
    )
)

gpt_o4_mini_deployment = az.cognitiveservices.Deployment(
    "gpt_o4_mini_deployment",
    account_name=openai_account_sweden.name,
    deployment_name="o4-mini",
    properties={
        "model": {
            "format": "OpenAI",
            "name": "o4-mini",
            "version": "2025-04-16",
        },
        "version_upgrade_option": az.cognitiveservices.DeploymentModelVersionUpgradeOption.ONCE_NEW_DEFAULT_VERSION_AVAILABLE,
    },
    resource_group_name=victor_sweden_resource_group.name,
    sku={
        "capacity": 100,
        "name": "GlobalStandard",
    },
    opts=OPTS,
)

gpt_41 = az.cognitiveservices.Deployment(
    "gpt_41",
    account_name=openai_account_sweden.name,
    deployment_name="gpt-4.1",
    properties={
        "model": {
            "format": "OpenAI",
            "name": "gpt-4.1",
            "version": "2025-04-14",
        },
        "version_upgrade_option": az.cognitiveservices.DeploymentModelVersionUpgradeOption.ONCE_NEW_DEFAULT_VERSION_AVAILABLE,
    },
    resource_group_name=victor_sweden_resource_group.name,
    sku={
        "capacity": 100,
        "name": "GlobalStandard",
    },
    opts=OPTS,
)

gpt_41_mini = az.cognitiveservices.Deployment(
    "gpt_41_mini",
    account_name=openai_account_sweden.name,
    deployment_name="gpt-4.1-mini",
    properties={
        "model": {
            "format": "OpenAI",
            "name": "gpt-4.1-mini",
            "version": "2025-04-14",
        },
        "version_upgrade_option": az.cognitiveservices.DeploymentModelVersionUpgradeOption.ONCE_NEW_DEFAULT_VERSION_AVAILABLE,
    },
    resource_group_name=victor_sweden_resource_group.name,
    sku={
        "capacity": 100,
        "name": "GlobalStandard",
    },
    opts=OPTS,
)

gpt_45 = az.cognitiveservices.Deployment(
    "gpt_45",
    account_name=openai_account_sweden.name,
    deployment_name="gpt-4.5",
    properties={
        "model": {
            "format": "OpenAI",
            "name": "gpt-4.5-preview",
            "version": "2025-02-27",
        },
        "version_upgrade_option": az.cognitiveservices.DeploymentModelVersionUpgradeOption.ONCE_NEW_DEFAULT_VERSION_AVAILABLE,
    },
    resource_group_name=victor_sweden_resource_group.name,
    sku={
        "capacity": 100,
        "name": "GlobalStandard",
    },
    opts=OPTS,
)

pulumi.export(
    "API: OpenAI: Endpoint", openai_account_sweden_details.properties.endpoint
)
pulumi.export("API: OpenAI: Key", pulumi.Output.secret(openai_keys_sweden.key1))
