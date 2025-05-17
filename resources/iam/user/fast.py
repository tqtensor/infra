import pulumi
import pulumi_aws as aws
from pulumi import Output

from resources.storage.bucket.s3 import fast_bucket
from resources.utils import get_options

OPTS = get_options(profile="personal", region="us-east-1", type="resource")


fast_user = aws.iam.User("fast_user", name="fast-user", force_destroy=True, opts=OPTS)

fast_s3_policy = aws.iam.Policy(
    "fast_s3_policy",
    policy=Output.json_dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": fast_bucket.arn,
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                    "Resource": fast_bucket.arn.apply(lambda arn: f"{arn}/*"),
                },
            ],
        }
    ),
    opts=OPTS,
)

fast_policy_attachment = aws.iam.UserPolicyAttachment(
    "fast_policy_attachment",
    user=fast_user.name,
    policy_arn=fast_s3_policy.arn,
    opts=OPTS,
)

fast_access_key = aws.iam.AccessKey("fast_access_key", user=fast_user.name, opts=OPTS)

pulumi.export("IAM: fast: access_key_id", fast_access_key.id)
pulumi.export("IAM: fast: secret_access_key", fast_access_key.secret)
