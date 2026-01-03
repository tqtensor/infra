import hashlib
import json

import pulumi
import pulumi_cloudflare as cloudflare

from resources.utils import get_options

OPTS = get_options(provider="cloudflare")


def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


account_id = pulumi.Config().require("cloudflareAccountId")

tqtensor_homelab_r2_token = cloudflare.ApiToken(
    "tqtensor_homelab_r2_token",
    name="tqtensor-homelab-r2-token",
    policies=[
        cloudflare.ApiTokenPolicyArgs(
            effect="allow",
            permission_groups=[
                cloudflare.ApiTokenPolicyPermissionGroupArgs(
                    id="2efd5506f9c8494dacb1fa10a3e7d5b6"
                )
            ],
            resources=json.dumps(
                {
                    f"com.cloudflare.edge.r2.bucket.{account_id}_default_tqtensor-homelab": "*"
                }
            ),
        )
    ],
    opts=OPTS,
)

pulumi.export("IAM: R2: tqtensor-homelab: Token ID", tqtensor_homelab_r2_token.id)
pulumi.export(
    "IAM: R2: tqtensor-homelab: Token Secret (SHA256)",
    tqtensor_homelab_r2_token.value.apply(sha256_hash),
)
