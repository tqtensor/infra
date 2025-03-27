import base64
import os

import pulumi_gcp as gcp
import yaml
from pulumi import Output

from resources.providers import gcp_pixelml_us_central_1
from resources.serverless import moondream2
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml",
    region="us-central-1",
    type="resource",
    provider="gcp",
)


def create_api_gateway(api_name: str, cloudrun_service: gcp.cloudrun.Service):
    api = gcp.apigateway.Api(
        "{}_api".format(api_name.replace("-", "_")),
        api_id=api_name,
        display_name=api_name,
        project="gen-lang-client-0608717027",
        opts=OPTS,
    )

    api_config_file_path = os.path.join(os.path.dirname(__file__), "replicate.yaml")
    config_document = yaml.safe_load(open(api_config_file_path, "r"))
    config_document["x-google-backend"]["address"] = cloudrun_service.statuses[0].url

    api_config = gcp.apigateway.ApiConfig(
        "{}_api_config".format(api_name.replace("-", "_")),
        api=api_name,
        api_config_id=api_name,
        display_name=api_name,
        openapi_documents=[
            {
                "document": {
                    "contents": Output.all(config_document).apply(
                        lambda args: base64.b64encode(
                            yaml.dump(args[0]).encode("utf-8")
                        ).decode("utf-8")
                    ),
                    "path": "replicate.yaml",
                },
            }
        ],
        project=Output.all(gcp_pixelml_us_central_1.project).apply(
            lambda args: args[0]
        ),
        opts=get_options(
            profile="pixelml",
            region="us-central-1",
            type="resource",
            provider="gcp",
            kwargs={"depends_on": [api]},
        ),
    )
    return api, api_config


moondream2_api, moondream2_api_config = create_api_gateway(
    api_name="moondream2", cloudrun_service=moondream2
)
