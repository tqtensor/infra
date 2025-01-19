import pulumi
import pulumi_aws as aws

from resources.s3 import duplicati_bucket
from resources.utils import get_options

OPTS = get_options(
    profile="personal", region="eu-central-1", type="resource", protect=False
)


def create_duplicati_user():
    duplicati_user = aws.iam.User(
        "duplicati_user", name="duplicati-user", force_destroy=True, opts=OPTS
    )

    duplicati_s3_policy = aws.iam.Policy(
        "duplicati_s3_policy",
        policy=pulumi.Output.json_dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:ListBucket"],
                        "Resource": duplicati_bucket.arn,
                    },
                    {
                        "Effect": "Allow",
                        "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                        "Resource": duplicati_bucket.arn.apply(lambda arn: f"{arn}/*"),
                    },
                ],
            }
        ),
        opts=OPTS,
    )

    duplicati_policy_attachment = aws.iam.UserPolicyAttachment(
        "duplicati_policy_attachment",
        user=duplicati_user.name,
        policy_arn=duplicati_s3_policy.arn,
        opts=OPTS,
    )

    duplicati_access_key = aws.iam.AccessKey(
        "duplicati_access_key", user=duplicati_user.name, opts=OPTS
    )

    pulumi.export("Duplicati: access_key_id:", duplicati_access_key.id)
    pulumi.export("Duplicati: secret_access_key:", duplicati_access_key.secret)
