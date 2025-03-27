import pulumi_gcp as gcp
from pulumi import Output

from resources.ecr import whisper_diarization_image_uri
from resources.iam import cloudrun_sa
from resources.providers import gcp_pixelml_us_central_1
from resources.utils import get_options

OPTS = get_options(
    profile="pixelml",
    region="us-central-1",
    type="resource",
    provider="gcp",
)


whisper_diarization = gcp.cloudrun.Service(
    "whisper_diarization",
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
    name="whisper-diarization",
    project=Output.all(
        gcp_pixelml_us_central_1.project,
    ).apply(lambda args: args[0]),
    template=Output.all(whisper_diarization_image_uri, cloudrun_sa.email).apply(
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
