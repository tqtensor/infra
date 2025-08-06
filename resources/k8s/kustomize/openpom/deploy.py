from pathlib import Path

import pulumi
from pulumi_kubernetes.kustomize import Directory

from resources.k8s.providers import k8s_provider_auto_pilot_eu_west_4

OPTS = pulumi.ResourceOptions(provider=k8s_provider_auto_pilot_eu_west_4)


def render_deployment(obj, opts):
    if obj["kind"] == "Deployment" and obj["apiVersion"] == "apps/v1":
        obj["spec"]["template"]["spec"]["containers"][0][
            "image"
        ] = "us-central1-docker.pkg.dev/gen-lang-client-0608717027/pixelml-us-central-1-registry/openpom:latest"

        obj["spec"]["template"]["spec"]["nodeSelector"] = {
            "cloud.google.com/gke-accelerator": "nvidia-tesla-t4",
            "cloud.google.com/gke-accelerator-count": "1",
        }

        obj["spec"]["template"]["spec"]["containers"][0]["resources"] = {
            "requests": {"nvidia.com/gpu": 1, "memory": "4Gi", "cpu": "2"},
            "limits": {"nvidia.com/gpu": 1, "memory": "8Gi", "cpu": "4"},
        }


base_dir = Path(__file__).parent / "base"

openpom_kustomize = Directory(
    "openpom_kustomize",
    directory=base_dir.as_posix(),
    transformations=[render_deployment],
    opts=OPTS,
)
