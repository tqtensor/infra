import pulumi_aws as aws
from pulumi import Output

from resources.storage.bucket.s3 import velero_bucket
from resources.utils import get_options

OPTS = get_options(profile="personal", region="us-east-1", type="resource")


velero_user = aws.iam.User(
    "velero_user", name="velero-user", force_destroy=True, opts=OPTS
)

velero_s3_policy = aws.iam.Policy(
    "velero_s3_policy",
    policy=Output.json_dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": velero_bucket.arn,
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                    "Resource": velero_bucket.arn.apply(lambda arn: f"{arn}/*"),
                },
            ],
        }
    ),
    opts=OPTS,
)

velero_policy_attachment = aws.iam.UserPolicyAttachment(
    "velero_policy_attachment",
    user=velero_user.name,
    policy_arn=velero_s3_policy.arn,
    opts=OPTS,
)

velero_access_key = aws.iam.AccessKey(
    "velero_access_key", user=velero_user.name, opts=OPTS
)
