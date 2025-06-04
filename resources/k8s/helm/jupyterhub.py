from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare.tls import jupyterhub_origin_ca_cert_bundle
from resources.ecr.docker.jupyterhub import jupyterhub_image_ref
from resources.k8s.providers import k8s_provider_auto_pilot_eu_west_4
from resources.utils import encode_tls_secret_data, fill_in_password

OPTS = pulumi.ResourceOptions(provider=k8s_provider_auto_pilot_eu_west_4)


jupyterhub_ns = k8s.core.v1.Namespace(
    "jupyterhub_ns", metadata={"name": "jupyterhub"}, opts=OPTS
)

jupyterhub_tls_secret = k8s.core.v1.Secret(
    "jupyterhub_tls_secret",
    metadata={
        "name": "jupyterhub-tls-secret",
        "namespace": jupyterhub_ns.metadata["name"],
    },
    data=Output.all(
        jupyterhub_origin_ca_cert_bundle[0].certificate,
        jupyterhub_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

secrets_file_path = Path(__file__).parent / "secrets" / "jupyterhub.yaml"
secret_values = fill_in_password(
    encrypted_yaml=secrets_file_path, value_path="dummy_password"
)

values_file_path = Path(__file__).parent / "values" / "jupyterhub.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    chart_values["hub"]["config"]["DummyAuthenticator"]["password"] = secret_values[
        "dummy_password"
    ]

    chart_values["singleuser"]["image"]["name"] = jupyterhub_image_ref.uri

jupyterhub_release = k8s.helm.v3.Release(
    "jupyterhub",
    k8s.helm.v3.ReleaseArgs(
        chart="jupyterhub",
        version="4.1.0",
        name="jupyterhub",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://hub.jupyter.org/helm-chart",
        ),
        namespace=jupyterhub_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_auto_pilot_eu_west_4,
        depends_on=[jupyterhub_ns],
    ),
)
