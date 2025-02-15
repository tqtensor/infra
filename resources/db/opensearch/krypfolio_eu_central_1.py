import json

import pulumi
import pulumi_aws as aws

from resources.providers import aws_krypfolio_eu_central_1
from resources.utils import get_options

OPTS = get_options(profile="krypfolio", region="eu-central-1", type="resource")

collection_name = "krp-ec1-os-collection"

krp_ec1_os_sec_policy = aws.opensearch.ServerlessSecurityPolicy(
    "krp_ec1_os_sec_policy",
    name="krp-ec1-os-sec-policy",
    type="encryption",
    policy=json.dumps(
        {
            "Rules": [
                {
                    "Resource": [f"collection/{collection_name}"],
                    "ResourceType": "collection",
                }
            ],
            "AWSOwnedKey": True,
        }
    ),
    opts=OPTS,
)

krp_ec1_os_colection = aws.opensearch.ServerlessCollection(
    "krp_ec1_os_colection",
    name=collection_name,
    opts=pulumi.ResourceOptions(
        depends_on=[krp_ec1_os_sec_policy],
        provider=aws_krypfolio_eu_central_1,
        protect=True,
    ),
)

pulumi.export(
    "OpenSearch: endpoint",
    krp_ec1_os_colection.collection_endpoint,
)
