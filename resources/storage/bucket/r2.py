import pulumi
import pulumi_cloudflare as cloudflare

from resources.utils import get_options

OPTS = get_options(provider="cloudflare")

tqtensor_homelab_bucket = cloudflare.R2Bucket(
    "tqtensor_homelab_bucket",
    account_id=pulumi.Config().require("cloudflareAccountId"),
    jurisdiction="default",
    location="WEUR",
    name="tqtensor-homelab",
    storage_class="Standard",
    opts=OPTS,
)

tqtensor_reddot_bucket = cloudflare.R2Bucket(
    "tqtensor_reddot_bucket",
    account_id=pulumi.Config().require("cloudflareAccountId"),
    jurisdiction="default",
    location="WEUR",
    name="tqtensor-reddot",
    storage_class="Standard",
    opts=OPTS,
)

tqtensor_reddot_bucket_cors = cloudflare.R2BucketCors(
    "tqtensor_reddot_bucket_cors",
    account_id=pulumi.Config().require("cloudflareAccountId"),
    bucket_name=tqtensor_reddot_bucket.name,
    rules=[
        {
            "allowed": {
                "methods": ["GET", "PUT", "POST", "DELETE"],
                "origins": ["chrome-extension://*"],
                "headers": ["*"],
            },
            "max_age_seconds": 3600,
            "id": "AllowChromeExtension",
        }
    ],
    opts=OPTS,
)
