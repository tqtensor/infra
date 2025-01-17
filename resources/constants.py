"""
Avoids accidental delete of resources.
"""

import pulumi
import pulumi_cloudflare as cloudflare

# Cloudflare
tqtensor_com = cloudflare.Zone.get(
    "tqtensor_com",
    id="1fa667eb57e3e586d4f0bd8b6cd2e7ad",
    account_id=pulumi.Config().require("accountId"),
)
