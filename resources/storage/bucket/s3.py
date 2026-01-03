import pulumi_aws as aws

from resources.utils import get_options

AS1_OPTS = get_options(profile="personal", region="ap-southeast-1", type="resource")
EC1_OPTS = get_options(profile="personal", region="eu-central-1", type="resource")
UE1_OPTS = get_options(profile="personal", region="us-east-1", type="resource")


arq_bucket = aws.s3.Bucket.get(
    "arq_bucket",
    id="tqtensor-arq-bucket-eu",
    bucket="tqtensor-arq-bucket-eu",
    opts=EC1_OPTS,
)

arq_bucket_lifecycle = aws.s3.BucketLifecycleConfiguration(
    "arq_bucket_lifecycle",
    bucket=arq_bucket.id,
    rules=[
        aws.s3.BucketLifecycleConfigurationRuleArgs(
            id="archive",
            status="Enabled",
            transitions=[
                aws.s3.BucketLifecycleConfigurationRuleTransitionArgs(
                    days=30, storage_class="INTELLIGENT_TIERING"
                ),
                aws.s3.BucketLifecycleConfigurationRuleTransitionArgs(
                    days=180, storage_class="DEEP_ARCHIVE"
                ),
            ],
        ),
    ],
    opts=EC1_OPTS,
)

fast_bucket = aws.s3.Bucket.get(
    "fast_bucket",
    id="tqtensor-fast-backup",
    bucket="tqtensor-fast-backup",
    opts=AS1_OPTS,
)

fast_bucket_lifecycle = aws.s3.BucketLifecycleConfiguration(
    "fast_bucket_lifecycle",
    bucket=fast_bucket.id,
    rules=[
        aws.s3.BucketLifecycleConfigurationRuleArgs(
            id="archive",
            status="Enabled",
            transitions=[
                aws.s3.BucketLifecycleConfigurationRuleTransitionArgs(
                    days=3,
                    storage_class="GLACIER",
                ),
            ],
        ),
    ],
    opts=AS1_OPTS,
)

pulumi_bucket = aws.s3.Bucket(
    "pulumi_bucket",
    bucket="tqtensor-pulumi-bucket-us",
    opts=UE1_OPTS,
)
