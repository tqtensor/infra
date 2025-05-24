import pulumi_aws as aws
from pulumi import Output

from resources.storage.bucket.s3 import mlflow_bucket
from resources.utils import get_options

OPTS = get_options(profile="personal", region="us-east-1", type="resource")


mlflow_user = aws.iam.User(
    "mlflow_user", name="mlflow-user", force_destroy=True, opts=OPTS
)

mlflow_s3_policy = aws.iam.Policy(
    "mlflow_s3_policy",
    policy=Output.json_dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": mlflow_bucket.arn,
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                    "Resource": mlflow_bucket.arn.apply(lambda arn: f"{arn}/*"),
                },
            ],
        }
    ),
    opts=OPTS,
)

mlflow_policy_attachment = aws.iam.UserPolicyAttachment(
    "mlflow_policy_attachment",
    user=mlflow_user.name,
    policy_arn=mlflow_s3_policy.arn,
    opts=OPTS,
)

mlflow_access_key = aws.iam.AccessKey(
    "mlflow_access_key", user=mlflow_user.name, opts=OPTS
)
