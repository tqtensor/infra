from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
from pulumi import Output
from pulumi_kubernetes.kustomize import Directory

from resources.cloudflare.tls import openpom_origin_ca_cert_bundle
from resources.k8s.providers import k8s_provider_auto_pilot_eu_west_4
from resources.utils import encode_tls_secret_data

OPTS = pulumi.ResourceOptions(provider=k8s_provider_auto_pilot_eu_west_4)


openpom_ns = k8s.core.v1.Namespace(
    "openpom_ns", metadata={"name": "openpom"}, opts=OPTS
)

openpom_tls_secret = k8s.core.v1.Secret(
    "openpom_tls_secret",
    metadata={"name": "openpom-tls-secret", "namespace": openpom_ns.metadata["name"]},
    data=Output.all(
        openpom_origin_ca_cert_bundle[0].certificate,
        openpom_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)


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
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_auto_pilot_eu_west_4,
        depends_on=[openpom_ns, openpom_tls_secret],
    ),
)
