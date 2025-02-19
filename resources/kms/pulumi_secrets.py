import pulumi
import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(
    profile="personal", region="us-east-1", type="resource", protect=False
)


pulumi_secrets_key = aws.kms.Key(
    "pulumi_secrets_key",
    deletion_window_in_days=14,
    opts=OPTS,
)

pulumi_secrets_key_alias = aws.kms.Alias(
    "pulumi_secrets_key_alias",
    name="alias/pulumi-secrets-key",
    target_key_id=pulumi_secrets_key.id,
    opts=OPTS,
)

pulumi.export("KMS: pulumi_secrets: ARN", pulumi_secrets_key.arn)
