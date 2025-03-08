import os

import pulumi
import pulumi_kubernetes as k8s
import pulumi_random as random
import yaml
from pulumi import Output

from resources.cloudflare import tei_origin_ca_cert, tei_private_key, tei_unifai_dev
from resources.k8s.providers import k8s_provider_auto_pilot_asia_east_1
from resources.utils import encode_tls_secret_data

OPTS = pulumi.ResourceOptions(provider=k8s_provider_auto_pilot_asia_east_1)


tei_ns = k8s.core.v1.Namespace(
    "tei_ns",
    metadata={"name": "tei"},
    opts=OPTS,
)

tei_tls_secret = k8s.core.v1.Secret(
    "tei_tls_secret",
    metadata={"name": "tei-tls-secret", "namespace": tei_ns.metadata["name"]},
    data=Output.all(
        tei_origin_ca_cert.certificate, tei_private_key.private_key_pem
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

values_file_path = os.path.join(os.path.dirname(__file__), "values", "tei.yaml")
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)
    chart_values["ingress"]["hosts"][0]["host"] = tei_unifai_dev.hostname
    chart_values["ingress"]["tls"][0]["hosts"][0] = tei_unifai_dev.hostname
    chart_values["env"] = [
        {
            "name": "API_KEY",
            "value": random.RandomPassword(
                "tei_api_key", special=False, length=32
            ).result,
        }
    ]

tei_release = k8s.helm.v3.Release(
    "tei",
    k8s.helm.v3.ReleaseArgs(
        chart="text-embeddings-inference",
        name="tei",
        version="0.1.8",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://infracloudio.github.io/charts",
        ),
        namespace=tei_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_auto_pilot_asia_east_1,
        depends_on=[tei_ns],
    ),
)
