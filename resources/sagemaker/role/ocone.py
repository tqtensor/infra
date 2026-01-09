import json

import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(profile="personal", region="eu-central-1", type="resource")


ocone_sagemaker_execution_role = aws.iam.Role(
    "ocone_sagemaker_execution_role",
    name="ocone-sagemaker-execution-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": [
                            "sagemaker.amazonaws.com",
                            "scheduler.amazonaws.com",
                        ]
                    },
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
    opts=OPTS,
)

OCONE_MANAGED_POLICIES = [
    "AmazonSageMakerFullAccess",
    "AmazonS3FullAccess",
    "AmazonEC2ContainerRegistryFullAccess",
]

ocone_policy_attachments = [
    aws.iam.RolePolicyAttachment(
        f"ocone_{policy.lower()}_attachment",
        role=ocone_sagemaker_execution_role.name,
        policy_arn=f"arn:aws:iam::aws:policy/{policy}",
        opts=OPTS,
    )
    for policy in OCONE_MANAGED_POLICIES
]
