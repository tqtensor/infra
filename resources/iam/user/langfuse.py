import pulumi_aws as aws
from pulumi import Output

from resources.storage.bucket.s3 import langfuse_bucket
from resources.utils import get_options

OPTS = get_options(profile="personal", region="eu-central-1", type="resource")


langfuse_user = aws.iam.User(
    "langfuse_user", name="langfuse-user", force_destroy=True, opts=OPTS
)

langfuse_s3_policy = aws.iam.Policy(
    "langfuse_s3_policy",
    policy=Output.json_dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": langfuse_bucket.arn,
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                    "Resource": langfuse_bucket.arn.apply(lambda arn: f"{arn}/*"),
                },
            ],
        }
    ),
    opts=OPTS,
)

langfuse_policy_attachment = aws.iam.UserPolicyAttachment(
    "langfuse_policy_attachment",
    user=langfuse_user.name,
    policy_arn=langfuse_s3_policy.arn,
    opts=OPTS,
)

langfuse_access_key = aws.iam.AccessKey(
    "langfuse_access_key", user=langfuse_user.name, opts=OPTS
)
