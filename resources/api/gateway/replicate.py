import base64
from pathlib import Path

import pulumi_gcp as gcp
import yaml
from pulumi import Output

from resources.providers import gcp_pixelml_us_central_1
from resources.serverless import whisper_diarization
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml",
    region="us-central-1",
    type="resource",
    provider="gcp",
    protect=False,
)


def create_api_gateway(api_name: str, cloudrun_service: gcp.cloudrun.Service):
    api = gcp.apigateway.Api(
        "{}_api".format(api_name.replace("-", "_")),
        api_id=api_name,
        display_name=api_name,
        project="gen-lang-client-0608717027",
        opts=OPTS,
    )

    api_config_file_path = Path(__file__).parent / "replicate.yaml"
    config_document = yaml.safe_load(open(api_config_file_path, "r"))
    config_document["info"]["title"] = api_name
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
            protect=False,
        ),
    )

    api_gateway = gcp.apigateway.Gateway(
        "{}_api_gateway".format(api_name.replace("-", "_")),
        api_config=api_config.id,
        display_name=api_name,
        gateway_id=api_name,
        project=Output.all(gcp_pixelml_us_central_1.project).apply(
            lambda args: args[0]
        ),
        region=Output.all(gcp_pixelml_us_central_1.region).apply(lambda args: args[0]),
        opts=get_options(
            profile="pixelml",
            region="us-central-1",
            type="resource",
            provider="gcp",
            kwargs={"depends_on": [api]},
            protect=False,
        ),
    )

    api_service = gcp.projects.Service(
        "{}_api_service".format(api_name.replace("-", "_")),
        service=api.managed_service,
        project=Output.all(gcp_pixelml_us_central_1.project).apply(
            lambda args: args[0]
        ),
        opts=get_options(
            profile="pixelml",
            region="us-central-1",
            type="resource",
            provider="gcp",
            kwargs={"depends_on": [api, api_config]},
            protect=False,
        ),
    )

    api_key = gcp.projects.ApiKey(
        "{}_api_key".format(api_name.replace("-", "_")),
        name=api_name,
        display_name=api_name,
        restrictions={
            "api_targets": [
                {
                    "service": api_service.service,
                }
            ],
        },
        opts=get_options(
            profile="pixelml",
            region="us-central-1",
            type="resource",
            provider="gcp",
            kwargs={"depends_on": [api_service]},
            protect=False,
        ),
    )
    return api, api_config, api_gateway, api_service, api_key


_ = create_api_gateway(
    api_name="whisper-diarization", cloudrun_service=whisper_diarization
)
