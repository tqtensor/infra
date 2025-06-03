import base64
from pathlib import Path

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare.tls import vllm_origin_ca_cert_bundle
from resources.k8s.providers import k8s_provider_auto_pilot_eu_west_4
from resources.utils import encode_tls_secret_data, fill_in_password

OPTS = pulumi.ResourceOptions(provider=k8s_provider_auto_pilot_eu_west_4)


vllm_ns = k8s.core.v1.Namespace("vllm_ns", metadata={"name": "vllm"}, opts=OPTS)

vllm_tls_secret = k8s.core.v1.Secret(
    "vllm_tls_secret",
    metadata={"name": "vllm-tls-secret", "namespace": vllm_ns.metadata["name"]},
    data=Output.all(
        vllm_origin_ca_cert_bundle[0].certificate,
        vllm_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

secrets_file_path = Path(__file__).parent / "secrets" / "vllm.yaml"
secret_values = fill_in_password(
    encrypted_yaml=secrets_file_path, value_path="hf_token"
)

vllm_api_key_secret = k8s.core.v1.Secret(
    "vllm_api_key_secret",
    metadata={"name": "vllm-api-key-secret", "namespace": vllm_ns.metadata["name"]},
    data=Output.all(secret_values["auth"]).apply(
        lambda args: {"auth": base64.b64encode(args[0].encode()).decode()}
    ),
    opts=OPTS,
)

values_file_path = Path(__file__).parent / "values" / "vllm.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    def apply_hf_token(token):
        for model in chart_values["servingEngineSpec"]["modelSpec"]:
            model["hf_token"] = token

    Output.all(secret_values["hf_token"]).apply(
        lambda args: apply_hf_token(token=args[0])
    )

vllm_release = k8s.helm.v3.Release(
    "vllm",
    k8s.helm.v3.ReleaseArgs(
        chart="vllm-stack",
        version="0.1.2",
        name="vllm",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://vllm-project.github.io/production-stack",
        ),
        namespace=vllm_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_auto_pilot_eu_west_4,
        depends_on=[vllm_ns, vllm_tls_secret],
    ),
)
