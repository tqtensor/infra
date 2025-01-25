import pulumi
import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(profile="personal", region="us-east-1", type="resource")


nextcloud_user = aws.iam.User(
    "nextcloud_user", name="nextcloud-user", force_destroy=True, opts=OPTS
)

nextcloud_s3_policy = aws.iam.Policy(
    "nextcloud_s3_policy",
    policy=pulumi.Output.json_dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": "arn:aws:s3:::tqtensor-nextcloud-eu",
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
                    "Resource": "arn:aws:s3:::tqtensor-nextcloud-eu/*",
                },
            ],
        }
    ),
    opts=OPTS,
)

nextcloud_policy_attachment = aws.iam.UserPolicyAttachment(
    "nextcloud_policy_attachment",
    user=nextcloud_user.name,
    policy_arn=nextcloud_s3_policy.arn,
    opts=OPTS,
)

nextcloud_access_key = aws.iam.AccessKey(
    "nextcloud_access_key", user=nextcloud_user.name, opts=OPTS
)

pulumi.export("Nextcloud: access_key_id", nextcloud_access_key.id)
pulumi.export("Nextcloud: secret_access_key", nextcloud_access_key.secret)
