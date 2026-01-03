"""
Avoids accidental delete of resources or circular dependencies.
"""

import pulumi
import pulumi_cloudflare as cloudflare

# Cloudflare
tqtensor_com = cloudflare.Zone.get(
    "tqtensor_com",
    id="1fa667eb57e3e586d4f0bd8b6cd2e7ad",
)

tqtensor_homelab_bucket = cloudflare.get_r2_bucket(
    account_id=pulumi.Config().require("cloudflareAccountId"),
    bucket_name="tqtensor-homelab",
)
