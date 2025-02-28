"""
Avoids accidental delete of resources.
"""

import pulumi
import pulumi_cloudflare as cloudflare

# Cloudflare
krypfolio_com = cloudflare.Zone.get(
    "krypfolio_com",
    id="04f429cac6262bf28db5731a84fde86a",
    account_id=pulumi.Config().require("accountId"),
)
mservice_dev = cloudflare.Zone.get(
    "mservice_dev",
    id="2a103726472fbfdf5fe1a6ba2121c723",
    account_id=pulumi.Config().require("accountId"),
)
tqtensor_com = cloudflare.Zone.get(
    "tqtensor_com",
    id="1fa667eb57e3e586d4f0bd8b6cd2e7ad",
    account_id=pulumi.Config().require("accountId"),
)
unifai_dev = cloudflare.Zone.get(
    "unifai_dev",
    id="e37a9e60005d57df4859fa4817c8128a",
    account_id=pulumi.Config().require("accountId"),
)
