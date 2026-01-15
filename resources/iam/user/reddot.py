import pulumi
import pulumi_aws as aws
from pulumi import Output

from resources.storage.bucket.reddot import reddot_recordings_bucket
from resources.utils import get_options

UE1_OPTS = get_options(profile="personal", region="us-east-1", type="resource")


reddot_extension_user = aws.iam.User(
    "reddot_extension_user",
    name="reddot-extension-user",
    opts=UE1_OPTS,
)

reddot_s3_policy = aws.iam.Policy(
    "reddot_s3_policy",
    name="reddot-extension-s3-policy",
    policy=Output.json_dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucket",
                    ],
                    "Resource": reddot_recordings_bucket.arn,
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObject",
                        "s3:GetObject",
                        "s3:AbortMultipartUpload",
                        "s3:ListMultipartUploadParts",
                    ],
                    "Resource": reddot_recordings_bucket.arn.apply(
                        lambda arn: f"{arn}/*"
                    ),
                },
            ],
        }
    ),
    opts=UE1_OPTS,
)

reddot_policy_attachment = aws.iam.UserPolicyAttachment(
    "reddot_policy_attachment",
    user=reddot_extension_user.name,
    policy_arn=reddot_s3_policy.arn,
    opts=UE1_OPTS,
)

reddot_access_key = aws.iam.AccessKey(
    "reddot_access_key",
    user=reddot_extension_user.name,
    opts=UE1_OPTS,
)

pulumi.export("IAM: RedDot Extension: access_key_id", reddot_access_key.id)
pulumi.export("IAM: RedDot Extension: secret_access_key", reddot_access_key.secret)
pulumi.export("S3: RedDot Extension: bucket_name", reddot_recordings_bucket.bucket)
pulumi.export("S3: RedDot Extension: bucket_region", "us-east-1")
