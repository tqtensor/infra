import json

import pulumi
import pulumi_aws as aws
from pulumi import Output

from resources.db import bedrock_secret
from resources.db.rds import krp_eu_central_1_rds_cluster
from resources.storage import n8n_bucket
from resources.utils import get_options

PER_EC1_OPTS = get_options(profile="personal", region="eu-central-1", type="resource")
KRP_EC1_OPTS = get_options(profile="krypfolio", region="eu-central-1", type="resource")


n8n_policy_llm_model = aws.iam.Policy(
    "n8n_policy_llm_model",
    name="n8n-policy-llm-model",
    policy=json.dumps(
        {
            "Statement": [
                {
                    "Action": ["bedrock:InvokeModel"],
                    "Effect": "Allow",
                    "Resource": [
                        "arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
                        "arn:aws:bedrock:eu-central-1::foundation-model/amazon.titan-embed-text-v1",
                    ],
                    "Sid": "BedrockInvokeModelStatement",
                }
            ],
            "Version": "2012-10-17",
        }
    ),
    opts=KRP_EC1_OPTS,
)

n8n_policy_rds = aws.iam.Policy(
    "n8n_policy_rds",
    name="n8n-policy-rds",
    policy=Output.all(krp_eu_central_1_rds_cluster.arn).apply(
        lambda args: json.dumps(
            {
                "Statement": [
                    {
                        "Action": ["rds:DescribeDBClusters"],
                        "Effect": "Allow",
                        "Resource": [args[0]],
                        "Sid": "RdsDescribeStatementID",
                    },
                    {
                        "Action": [
                            "rds-data:BatchExecuteStatement",
                            "rds-data:ExecuteStatement",
                        ],
                        "Effect": "Allow",
                        "Resource": [args[0]],
                        "Sid": "DataAPIStatementID",
                    },
                ],
                "Version": "2012-10-17",
            }
        )
    ),
    opts=KRP_EC1_OPTS,
)

n8n_policy_s3 = aws.iam.Policy(
    "n8n_policy_s3",
    name="n8n-policy-s3",
    policy=Output.all(
        aws.get_caller_identity(
            opts=pulumi.InvokeOptions(parent=n8n_policy_llm_model)
        ).account_id,
        aws.get_caller_identity(
            opts=pulumi.InvokeOptions(parent=n8n_bucket)
        ).account_id,
        n8n_bucket.arn,
    ).apply(
        lambda args: json.dumps(
            {
                "Statement": [
                    {
                        "Action": ["s3:ListBucket"],
                        "Condition": {
                            "StringEquals": {"aws:ResourceAccount": [args[0], args[1]]}
                        },
                        "Effect": "Allow",
                        "Resource": [args[2]],
                        "Sid": "S3ListBucketStatement",
                    },
                    {
                        "Action": ["s3:GetObject"],
                        "Condition": {
                            "StringEquals": {"aws:ResourceAccount": [args[0], args[1]]}
                        },
                        "Effect": "Allow",
                        "Resource": [f"{args[2]}/*"],
                        "Sid": "S3GetObjectStatement",
                    },
                ],
                "Version": "2012-10-17",
            }
        )
    ),
    opts=KRP_EC1_OPTS,
)

n8n_policy_secrets = aws.iam.Policy(
    "n8n_policy_secrets",
    name="n8n-policy-secrets",
    policy=Output.all(
        bedrock_secret.arn,
    ).apply(
        lambda args: json.dumps(
            {
                "Statement": [
                    {
                        "Action": ["secretsmanager:GetSecretValue"],
                        "Effect": "Allow",
                        "Resource": [args[0]],
                        "Sid": "SecretsManagerGetStatement",
                    }
                ],
                "Version": "2012-10-17",
            }
        )
    ),
    opts=KRP_EC1_OPTS,
)

n8n_role = aws.iam.Role(
    "n8n_role",
    assume_role_policy=Output.all(
        aws.get_caller_identity(
            opts=pulumi.InvokeOptions(parent=n8n_policy_llm_model)
        ).account_id
    ).apply(
        lambda args: json.dumps(
            {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "ArnLike": {
                                "aws:SourceArn": f"arn:aws:bedrock:eu-central-1:{args[0]}:knowledge-base/*"
                            },
                            "StringEquals": {"aws:SourceAccount": args[0]},
                        },
                        "Effect": "Allow",
                        "Principal": {"Service": "bedrock.amazonaws.com"},
                        "Sid": "AmazonBedrockKnowledgeBaseTrustPolicy",
                    }
                ],
                "Version": "2012-10-17",
            }
        )
    ),
    managed_policy_arns=[
        n8n_policy_llm_model.arn,
        n8n_policy_rds.arn,
        n8n_policy_s3.arn,
        n8n_policy_secrets.arn,
    ],
    name="n8n-role",
    opts=KRP_EC1_OPTS,
)

n8n_bucket_policy = aws.s3.BucketPolicy(
    "n8n_bucket_policy",
    bucket=n8n_bucket.id,
    policy=Output.all(n8n_role.arn, n8n_bucket.id).apply(
        lambda args: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": args[0]},
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:ListBucket",
                            "s3:DeleteObject",
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{args[1]}",
                            f"arn:aws:s3:::{args[1]}/*",
                        ],
                    }
                ],
            }
        )
    ),
    opts=PER_EC1_OPTS,
)
