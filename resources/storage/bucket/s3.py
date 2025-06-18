import json

import pulumi_aws as aws
from pulumi import Output

from resources.constants import stx_iam_user
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

arq_bucket_lifecycle = aws.s3.BucketLifecycleConfigurationV2(
    "arq_bucket_lifecycle",
    bucket=arq_bucket.id,
    rules=[
        aws.s3.BucketLifecycleConfigurationV2RuleArgs(
            id="archive",
            status="Enabled",
            transitions=[
                aws.s3.BucketLifecycleRuleTransitionArgs(
                    days=30, storage_class="INTELLIGENT_TIERING"
                ),
                aws.s3.BucketLifecycleRuleTransitionArgs(
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

fast_bucket_lifecycle = aws.s3.BucketLifecycleConfigurationV2(
    "fast_bucket_lifecycle",
    bucket=fast_bucket.id,
    rules=[
        aws.s3.BucketLifecycleConfigurationV2RuleArgs(
            id="archive",
            status="Enabled",
            transitions=[
                aws.s3.BucketLifecycleRuleTransitionArgs(
                    days=3,
                    storage_class="GLACIER",
                ),
            ],
        ),
    ],
    opts=AS1_OPTS,
)

mlflow_bucket = aws.s3.Bucket(
    "mlflow_bucket",
    bucket="tqtensor-mlflow-bucket-eu",
    acl="private",
    opts=EC1_OPTS,
)

mlflow_stx_bucket_policy = aws.s3.BucketPolicy(
    "mlflow_stx_bucket_policy",
    bucket=mlflow_bucket.id,
    policy=Output.all(stx_iam_user.arn, mlflow_bucket.arn).apply(
        lambda args: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": args[0]},
                        "Action": ["s3:ListBucket"],
                        "Resource": args[1],
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": args[0]},
                        "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                        "Resource": args[1] + "/*",
                    },
                ],
            }
        )
    ),
    opts=EC1_OPTS,
)

pulumi_bucket = aws.s3.Bucket(
    "pulumi_bucket",
    bucket="tqtensor-pulumi-bucket-us",
    acl="private",
    opts=UE1_OPTS,
)

velero_bucket = aws.s3.Bucket(
    "velero_bucket",
    bucket="tqtensor-velero-bucket-eu",
    acl="private",
    opts=EC1_OPTS,
)
