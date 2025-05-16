import pulumi_azure_native as az
from pulumi import Output

from resources.providers.az import az_quickqr_sweden
from resources.resource_group.sweden import victor_resource_group
from resources.utils import get_options

OPTS = get_options(profile="quickqr", region="sweden", type="resource", provider="az")


s3gw_storage_account = az.storage.StorageAccount(
    "s3gw_storage_account",
    account_name="s3gwdev",
    resource_group_name=victor_resource_group.name,
    location=az_quickqr_sweden.get_provider(module_member="location"),
    sku=az.storage.SkuArgs(
        name="Standard_LRS",
    ),
    kind="StorageV2",
    enable_https_traffic_only=True,
    opts=OPTS,
)

s3gw_blob_container = az.storage.BlobContainer(
    "s3gw_blob_container",
    container_name="s3gwdev-bucket",
    resource_group_name=victor_resource_group.name,
    account_name=s3gw_storage_account.name,
    public_access=az.storage.PublicAccess.NONE,
    opts=OPTS,
)

s3gw_storage_keys = Output.all(
    s3gw_storage_account.name, victor_resource_group.name
).apply(
    lambda args: az.storage.list_storage_account_keys(
        resource_group_name=args[1], account_name=args[0]
    )
)
