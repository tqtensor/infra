"""
Avoids accidental delete of resources or circular dependencies.
"""

import pulumi
import pulumi_aws as aws
import pulumi_cloudflare as cloudflare

from resources.utils import get_options

# AWS
stx_iam_user = aws.iam.User.get(
    "stx_iam_user",
    id="thaitang",
    opts=get_options(profile="stx", region="us-east-1", type="resource"),
)

# Cloudflare
tqtensor_com = cloudflare.Zone.get(
    "tqtensor_com",
    id="1fa667eb57e3e586d4f0bd8b6cd2e7ad",
    account_id=pulumi.Config().require("cloudflareAccountId"),
)
