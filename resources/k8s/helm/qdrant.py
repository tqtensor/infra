from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare.tls import qdrant_origin_ca_cert_bundle
from resources.k8s.providers import k8s_provider_par_2
from resources.utils import encode_tls_secret_data, fill_in_password

OPTS = pulumi.ResourceOptions(provider=k8s_provider_par_2)


qdrant_ns = k8s.core.v1.Namespace("qdrant_ns", metadata={"name": "qdrant"}, opts=OPTS)

secrets_file_path = Path(__file__).parent / "secrets" / "qdrant.yaml"
secret_values = fill_in_password(
    encrypted_yaml=secrets_file_path, value_path="apiKey", prefix="sk"
)

qdrant_tls_secret = k8s.core.v1.Secret(
    "qdrant_tls_secret",
    metadata={"name": "qdrant-tls-secret", "namespace": qdrant_ns.metadata["name"]},
    data=Output.all(
        qdrant_origin_ca_cert_bundle[0].certificate,
        qdrant_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = Path(__file__).parent / "values" / "qdrant.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    chart_values["apiKey"] = secret_values["apiKey"]

qdrant_release = k8s.helm.v3.Release(
    "qdrant",
    k8s.helm.v3.ReleaseArgs(
        chart="qdrant",
        version="1.14.1",
        name="qdrant",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://qdrant.github.io/qdrant-helm",
        ),
        namespace=qdrant_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_par_2,
        depends_on=[qdrant_ns, qdrant_tls_secret],
    ),
)
