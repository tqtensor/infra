import json

import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(
    profile="krypfolio", region="eu-central-1", type="resource", protect=False
)


n8n_role = aws.iam.Role(
    "n8n_role",
    name="n8n-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "bedrock.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
    opts=OPTS,
)

n8n_bedrock_policy = aws.iam.Policy(
    "n8n_bedrock_policy",
    name="n8n-bedrock-policy",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["bedrock:*"], "Resource": "*"}
            ],
        }
    ),
    opts=OPTS,
)

n8n_aoss_policy = aws.iam.Policy(
    "n8n_aoss_policy",
    name="n8n-aoss-policy",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["aoss:*"],
                    "Resource": "*",
                }
            ],
        }
    ),
    opts=OPTS,
)

n8n_bedrock_role_policy_attachment = aws.iam.RolePolicyAttachment(
    "n8n_bedrock_role_policy_attachment",
    role=n8n_role.name,
    policy_arn=n8n_bedrock_policy.arn,
    opts=OPTS,
)

n8n_aoss_role_policy_attachment = aws.iam.RolePolicyAttachment(
    "n8n_aoss_role_policy_attachment",
    role=n8n_role.name,
    policy_arn=n8n_aoss_policy.arn,
    opts=OPTS,
)
