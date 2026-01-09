import pulumi
import pulumi_cloudflare as cloudflare

from resources.constants import tqtensor_com
from resources.storage.bucket.r2 import tqtensor_homelab_bucket
from resources.utils import get_options

OPTS = get_options(provider="cloudflare")


delivery_tqtensor_com_r2_custom_domain = cloudflare.R2CustomDomain(
    "delivery_tqtensor_com_r2_custom_domain",
    account_id=pulumi.Config().require("cloudflareAccountId"),
    bucket_name=tqtensor_homelab_bucket.name,
    domain="delivery.tqtensor.com",
    enabled=True,
    zone_id=tqtensor_com.id,
    min_tls="1.2",
    opts=OPTS,
)
