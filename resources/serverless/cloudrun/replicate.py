from pathlib import Path

import pulumi_gcp as gcp
import yaml
from pulumi import Output

from resources.constants import ind_cloudrun_sa
from resources.ecr import replicate_image_uris
from resources.providers import gcp_pixelml_us_central_1
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml",
    region="us-central-1",
    type="resource",
    provider="gcp",
)


def deploy_replicate_service(image_name: str, hash: str) -> gcp.cloudrun.Service:
    service_name = image_name.replace(".", "-")

    service = gcp.cloudrun.Service(
        service_name.replace("-", "_"),
        location=Output.all(
            gcp_pixelml_us_central_1.region,
        ).apply(lambda args: args[0]),
        metadata=Output.all(
            gcp_pixelml_us_central_1.project,
        ).apply(
            lambda args: {
                "namespace": args[0],
            }
        ),
        name=service_name,
        project=Output.all(
            gcp_pixelml_us_central_1.project,
        ).apply(lambda args: args[0]),
        template=Output.all(
            replicate_image_uris[image_name][hash],
            ind_cloudrun_sa.email,
        ).apply(
            lambda args: {
                "metadata": {
                    "annotations": {
                        "autoscaling.knative.dev/maxScale": "5",
                        "run.googleapis.com/client-name": "gcloud",
                        "run.googleapis.com/cpu-throttling": "false",
                        "run.googleapis.com/execution-environment": "gen2",
                        "run.googleapis.com/gpu-zonal-redundancy-disabled": "true",
                        "run.googleapis.com/startup-cpu-boost": "true",
                    },
                    "labels": {
                        "run.googleapis.com/startupProbeType": "Default",
                    },
                },
                "spec": {
                    "container_concurrency": 80,
                    "containers": [
                        {
                            "image": args[0],
                            "ports": [
                                {
                                    "container_port": 5000,
                                    "name": "http1",
                                }
                            ],
                            "resources": {
                                "limits": {
                                    "cpu": "4",
                                    "memory": "16Gi",
                                    "nvidia.com/gpu": "1",
                                },
                            },
                            "startup_probe": {
                                "failure_threshold": 1,
                                "period_seconds": 240,
                                "tcp_socket": {
                                    "port": 5000,
                                },
                                "timeout_seconds": 240,
                            },
                        }
                    ],
                    "node_selector": {
                        "run.googleapis.com/accelerator": "nvidia-l4",
                    },
                    "service_account_name": args[1],
                    "timeout_seconds": 300,
                },
            }
        ),
        traffics=[
            {
                "latest_revision": True,
                "percent": 100,
            }
        ],
        opts=OPTS,
    )
    return service


configs = yaml.safe_load(open(Path(__file__).parent / "configs.yaml", "r").read())
for image_name, hash in configs.items():
    service_name = image_name.replace("-", "_").replace(".", "_")
    exec(
        f"""{service_name} = deploy_replicate_service(
        image_name=image_name,
        hash=hash,
    )"""
    )
