import pulumi_aws as aws

from resources.utils import get_options

UE1_OPTS = get_options(profile="personal", region="us-east-1", type="resource")


reddot_recordings_bucket = aws.s3.Bucket(
    "reddot_recordings_bucket",
    bucket="tqtensor-reddot-recordings",
    opts=UE1_OPTS,
)

reddot_recordings_bucket_cors = aws.s3.BucketCorsConfiguration(
    "reddot_recordings_bucket_cors",
    bucket=reddot_recordings_bucket.id,
    cors_rules=[
        aws.s3.BucketCorsConfigurationCorsRuleArgs(
            allowed_headers=["*"],
            allowed_methods=["GET", "PUT", "POST", "DELETE"],
            allowed_origins=["chrome-extension://*"],
            max_age_seconds=3600,
        )
    ],
    opts=UE1_OPTS,
)

reddot_recordings_bucket_public_access_block = aws.s3.BucketPublicAccessBlock(
    "reddot_recordings_bucket_public_access_block",
    bucket=reddot_recordings_bucket.id,
    block_public_acls=True,
    block_public_policy=True,
    ignore_public_acls=True,
    restrict_public_buckets=True,
    opts=UE1_OPTS,
)

reddot_recordings_bucket_accelerate = aws.s3.BucketAccelerateConfiguration(
    "reddot_recordings_bucket_accelerate",
    bucket=reddot_recordings_bucket.id,
    status="Enabled",
    opts=UE1_OPTS,
)

reddot_recordings_bucket_lifecycle = aws.s3.BucketLifecycleConfiguration(
    "reddot_recordings_bucket_lifecycle",
    bucket=reddot_recordings_bucket.id,
    rules=[
        aws.s3.BucketLifecycleConfigurationRuleArgs(
            id="archive-old-recordings",
            status="Enabled",
            transitions=[
                aws.s3.BucketLifecycleConfigurationRuleTransitionArgs(
                    days=30, storage_class="INTELLIGENT_TIERING"
                ),
                aws.s3.BucketLifecycleConfigurationRuleTransitionArgs(
                    days=90, storage_class="GLACIER"
                ),
            ],
        ),
    ],
    opts=UE1_OPTS,
)
