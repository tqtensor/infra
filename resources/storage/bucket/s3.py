import pulumi_aws as aws

from resources.utils import get_options

EC1_OPTS = get_options(
    profile="personal", region="eu-central-1", type="resource", protect=False
)
UE1_OPTS = get_options(
    profile="personal", region="us-east-1", type="resource", protect=False
)


arq_bucket = aws.s3.Bucket(
    "arq_bucket",
    bucket="tqtensor-arq-bucket-eu",
    acl="private",
    lifecycle_rules=[
        aws.s3.BucketLifecycleRuleArgs(
            enabled=True,
            transitions=[
                aws.s3.BucketLifecycleRuleTransitionArgs(
                    days=30, storage_class="INTELLIGENT_TIERING"
                ),
                aws.s3.BucketLifecycleRuleTransitionArgs(
                    days=180, storage_class="DEEP_ARCHIVE"
                ),
            ],
        )
    ],
    opts=EC1_OPTS,
)

n8n_bucket = aws.s3.Bucket(
    "n8n_bucket",
    bucket="tqtensor-n8n-bucket-eu",
    acl="private",
    opts=EC1_OPTS,
)

pulumi_bucket = aws.s3.Bucket(
    "pulumi_bucket",
    bucket="tqtensor-pulumi-bucket-us",
    acl="private",
    opts=UE1_OPTS,
)
