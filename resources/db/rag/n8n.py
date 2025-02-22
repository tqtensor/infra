import pulumi
import pulumi_aws as aws
from pulumi import Output

from resources.db.psql import bedrock_secret
from resources.db.rds import krp_ec1_rds_cluster
from resources.iam import n8n_role
from resources.storage import n8n_bucket
from resources.utils import get_options

OPTS = get_options(profile="krypfolio", region="eu-central-1", type="resource")


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
    storage_configuration=Output.all(bedrock_secret.arn, krp_ec1_rds_cluster.arn).apply(
        lambda args: {
            "rds_configuration": {
                "credentials_secret_arn": args[0],
                "database_name": "bedrock_db",
                "field_mapping": {
                    "metadata_field": "metadata",
                    "primary_key_field": "id",
                    "text_field": "chunks",
                    "vector_field": "embedding",
                },
                "resource_arn": args[1],
                "table_name": "bedrock_tbl",
            },
            "type": "RDS",
        }
    ),
    opts=OPTS,
)

n8n_kb_data_source = aws.bedrock.AgentDataSource(
    "n8n_kb_data_source",
    data_deletion_policy="DELETE",
    data_source_configuration=Output.all(
        n8n_bucket.arn,
        aws.get_caller_identity(
            opts=pulumi.InvokeOptions(parent=n8n_bucket)
        ).account_id,
    ).apply(
        lambda args: {
            "s3_configuration": {
                "bucket_arn": args[0],
                "bucket_owner_account_id": args[1],
            },
            "type": "S3",
        }
    ),
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
                "model_arn": "arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
            },
            "parsing_strategy": "BEDROCK_FOUNDATION_MODEL",
        },
    },
    opts=get_options(
        profile="krypfolio",
        region="eu-central-1",
        type="resource",
        kwargs={"depends_on": [n8n_kb_agent]},
    ),
)
