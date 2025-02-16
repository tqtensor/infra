# import pulumi_aws as aws
# from pulumi import Output

# from resources.db import krp_ec1_os_colection
# from resources.iam import n8n_role
# from resources.utils import get_options

# OPTS = get_options(
#     profile="krypfolio", region="eu-central-1", type="resource", protect=False
# )


# n8n_kb_agent = aws.bedrock.AgentKnowledgeBase(
#     "n8n_kb_agent",
#     name="n8n-kb-agent",
#     role_arn=n8n_role.arn,
#     knowledge_base_configuration={
#         "vector_knowledge_base_configuration": {
#             "embedding_model_arn": "arn:aws:bedrock:eu-central-1::foundation-model/amazon.titan-embed-text-v2:0",
#         },
#         "type": "VECTOR",
#     },
#     storage_configuration=Output.all(krp_ec1_os_colection.arn).apply(
#         lambda args: {
#             "type": "OPENSEARCH_SERVERLESS",
#             "opensearch_serverless_configuration": {
#                 "collection_arn": args[0],
#                 "vector_index_name": "n8n-kb-agent-index",
#                 "field_mapping": {
#                     "vector_field": "vector",
#                     "text_field": "text",
#                     "metadata_field": "metadata",
#                 },
#             },
#         }
#     ),
#     opts=OPTS,
# )
