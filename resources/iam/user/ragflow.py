import pulumi_aws as aws
from pulumi import Output

from resources.utils import get_options

OPTS = get_options(profile="personal", region="us-east-1", type="resource")


ragflow_s3_user = aws.iam.User(
    "ragflow_s3_user", name="ragflow-s3-user", force_destroy=True, opts=OPTS
)

ragflow_s3_policy = aws.iam.Policy(
    "ragflow_s3_policy",
    policy=Output.json_dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": "arn:aws:s3:::tqtensor-ragflow-bucket-eu",
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                    "Resource": "arn:aws:s3:::tqtensor-ragflow-bucket-eu/*",
                },
            ],
        }
    ),
    opts=OPTS,
)

ragflow_s3_policy_attachment = aws.iam.UserPolicyAttachment(
    "ragflow_s3_policy_attachment",
    user=ragflow_s3_user.name,
    policy_arn=ragflow_s3_policy.arn,
    opts=OPTS,
)

ragflow_s3_access_key = aws.iam.AccessKey(
    "ragflow_s3_access_key", user=ragflow_s3_user.name, opts=OPTS
)
