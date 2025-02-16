import json

import pulumi_aws as aws
from pulumi import Output

from resources.iam import n8n_role
from resources.utils import get_options

OPTS = get_options(profile="personal", region="eu-central-1", type="resource")


arq_bucket = aws.s3.Bucket(
    "arq_bucket",
    bucket="tqtensor-arq-bucket-eu",
    acl="private",
    opts=OPTS,
)

n8n_bucket = aws.s3.Bucket(
    "n8n_bucket",
    bucket="tqtensor-n8n-bucket-eu",
    acl="private",
    opts=OPTS,
)

n8n_bucket_policy = aws.s3.BucketPolicy(
    "n8n_bucket_policy",
    bucket=n8n_bucket.id,
    policy=Output.all(n8n_role.arn, n8n_bucket.id).apply(
        lambda args: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": args[0]},
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:ListBucket",
                            "s3:DeleteObject",
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{args[1]}",
                            f"arn:aws:s3:::{args[1]}/*",
                        ],
                    }
                ],
            }
        )
    ),
    opts=OPTS,
)
