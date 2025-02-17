import json

import pulumi_aws as aws

from resources.utils import get_options

OPTS = get_options(
    profile="krypfolio", region="eu-central-1", type="resource", protect=False
)


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
                        "arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
                        "arn:aws:bedrock:eu-central-1::foundation-model/amazon.titan-embed-text-v1",
                    ],
                    "Sid": "BedrockInvokeModelStatement",
                }
            ],
            "Version": "2012-10-17",
        }
    ),
    opts=OPTS,
)

n8n_policy_rds = aws.iam.Policy(
    "n8n_policy_rds",
    name="n8n-policy-rds",
    policy=json.dumps(
        {
            "Statement": [
                {
                    "Action": ["rds:DescribeDBClusters"],
                    "Effect": "Allow",
                    "Resource": [
                        "arn:aws:rds:eu-central-1:767397766072:cluster:krypfolio-eu-central-1-rds-cluster"
                    ],
                    "Sid": "RdsDescribeStatementID",
                },
                {
                    "Action": [
                        "rds-data:BatchExecuteStatement",
                        "rds-data:ExecuteStatement",
                    ],
                    "Effect": "Allow",
                    "Resource": [
                        "arn:aws:rds:eu-central-1:767397766072:cluster:krypfolio-eu-central-1-rds-cluster"
                    ],
                    "Sid": "DataAPIStatementID",
                },
            ],
            "Version": "2012-10-17",
        }
    ),
    opts=OPTS,
)

n8n_policy_s3 = aws.iam.Policy(
    "n8n_policy_s3",
    name="n8n-policy-s3",
    policy=json.dumps(
        {
            "Statement": [
                {
                    "Action": ["s3:ListBucket"],
                    "Condition": {
                        "StringEquals": {
                            "aws:ResourceAccount": ["767397766072", "100874337694"]
                        }
                    },
                    "Effect": "Allow",
                    "Resource": ["arn:aws:s3:::tqtensor-n8n-bucket-eu"],
                    "Sid": "S3ListBucketStatement",
                },
                {
                    "Action": ["s3:GetObject"],
                    "Condition": {
                        "StringEquals": {
                            "aws:ResourceAccount": ["767397766072", "100874337694"]
                        }
                    },
                    "Effect": "Allow",
                    "Resource": ["arn:aws:s3:::tqtensor-n8n-bucket-eu/*"],
                    "Sid": "S3GetObjectStatement",
                },
            ],
            "Version": "2012-10-17",
        }
    ),
    opts=OPTS,
)

n8n_policy_secrets = aws.iam.Policy(
    "n8n_policy_secrets",
    name="n8n-policy-secrets",
    policy=json.dumps(
        {
            "Statement": [
                {
                    "Action": ["secretsmanager:GetSecretValue"],
                    "Effect": "Allow",
                    "Resource": [
                        "arn:aws:secretsmanager:eu-central-1:767397766072:secret:bedrock-db-credentials-bb4630d-zGN7Ci"
                    ],
                    "Sid": "SecretsManagerGetStatement",
                }
            ],
            "Version": "2012-10-17",
        }
    ),
    opts=OPTS,
)

n8n_role = aws.iam.Role(
    "n8n_role",
    assume_role_policy=json.dumps(
        {
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "ArnLike": {
                            "aws:SourceArn": "arn:aws:bedrock:eu-central-1:767397766072:knowledge-base/*"
                        },
                        "StringEquals": {"aws:SourceAccount": "767397766072"},
                    },
                    "Effect": "Allow",
                    "Principal": {"Service": "bedrock.amazonaws.com"},
                    "Sid": "AmazonBedrockKnowledgeBaseTrustPolicy",
                }
            ],
            "Version": "2012-10-17",
        }
    ),
    managed_policy_arns=[
        n8n_policy_llm_model.arn,
        n8n_policy_rds.arn,
        n8n_policy_s3.arn,
        n8n_policy_secrets.arn,
    ],
    name="n8n-role",
    opts=OPTS,
)
