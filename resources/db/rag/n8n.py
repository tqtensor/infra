import pulumi
import pulumi_aws as aws

from resources.iam import n8n_role
from resources.providers import aws_krypfolio_eu_central_1
from resources.utils import get_options

OPTS = get_options(
    profile="krypfolio", region="eu-central-1", type="resource", protect=False
)


n8n_kb_agent = aws.bedrock.AgentKnowledgeBase(
    "n8n_kb_agent",
    knowledge_base_configuration={
        "type": "VECTOR",
        "vector_knowledge_base_configuration": {
            "embedding_model_arn": "arn:aws:bedrock:eu-central-1::foundation-model/amazon.titan-embed-text-v1",
        },
    },
    name="n8n-kb-agent",
    role_arn=n8n_role.arn,
    storage_configuration={
        "rds_configuration": {
            "credentials_secret_arn": "arn:aws:secretsmanager:eu-central-1:767397766072:secret:bedrock-db-credentials-bb4630d-zGN7Ci",
            "database_name": "bedrock_db",
            "field_mapping": {
                "metadata_field": "metadata",
                "primary_key_field": "id",
                "text_field": "chunks",
                "vector_field": "embedding",
            },
            "resource_arn": "arn:aws:rds:eu-central-1:767397766072:cluster:krypfolio-eu-central-1-rds-cluster",
            "table_name": "bedrock_tbl",
        },
        "type": "RDS",
    },
    opts=OPTS,
)

n8n_kb_data_source = aws.bedrock.AgentDataSource(
    "n8n_kb_data_source",
    data_deletion_policy="DELETE",
    data_source_configuration={
        "s3_configuration": {
            "bucket_arn": "arn:aws:s3:::tqtensor-n8n-bucket-eu",
            "bucket_owner_account_id": "100874337694",
        },
        "type": "S3",
    },
    knowledge_base_id=n8n_kb_agent.id,
    name="n8n-kb-data-source",
    vector_ingestion_configuration={
        "chunking_configuration": {
            "chunking_strategy": "SEMANTIC",
            "semantic_chunking_configuration": {
                "breakpoint_percentile_threshold": 95,
                "buffer_size": 0,
                "max_token": 300,
            },
        },
        "parsing_configuration": {
            "bedrock_foundation_model_configuration": {
                "model_arn": "arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
            },
            "parsing_strategy": "BEDROCK_FOUNDATION_MODEL",
        },
    },
    opts=pulumi.ResourceOptions(
        provider=aws_krypfolio_eu_central_1, depends_on=[n8n_kb_agent], protect=False
    ),
)
