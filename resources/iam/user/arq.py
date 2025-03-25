import pulumi
import pulumi_aws as aws
from pulumi import Output

from resources.storage.bucket.s3 import arq_bucket
from resources.utils import get_options

OPTS = get_options(profile="personal", region="eu-central-1", type="resource")


arq_user = aws.iam.User("arq_user", name="arq-user", opts=OPTS)

arq_s3_policy = aws.iam.Policy(
    "arq_s3_policy",
    policy=Output.json_dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
                    "Resource": arq_bucket.arn,
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                    "Resource": arq_bucket.arn.apply(lambda arn: f"{arn}/*"),
                },
            ],
        }
    ),
    opts=OPTS,
)

arq_policy_attachment = aws.iam.UserPolicyAttachment(
    "arq_policy_attachment",
    user=arq_user.name,
    policy_arn=arq_s3_policy.arn,
    opts=OPTS,
)

arq_access_key = aws.iam.AccessKey("arq_access_key", user=arq_user.name, opts=OPTS)

pulumi.export("IAM: Arq: access_key_id", arq_access_key.id)
pulumi.export("IAM: Arq: secret_access_key", arq_access_key.secret)
