from pathlib import Path
from typing import Dict

import pulumi
import pulumi_kubernetes as k8s
import yaml
from pulumi import Output

from resources.cloudflare.tls import langfuse_origin_ca_cert_bundle
from resources.k8s.providers import k8s_provider_par_2
from resources.utils import encode_tls_secret_data, fill_in_password

OPTS = pulumi.ResourceOptions(provider=k8s_provider_par_2)


langfuse_ns = k8s.core.v1.Namespace(
    "langfuse_ns", metadata={"name": "langfuse"}, opts=OPTS
)

langfuse_tls_secret = k8s.core.v1.Secret(
    "langfuse_tls_secret",
    metadata={"name": "langfuse-tls-secret", "namespace": langfuse_ns.metadata["name"]},
    data=Output.all(
        langfuse_origin_ca_cert_bundle[0].certificate,
        langfuse_origin_ca_cert_bundle[1].private_key_pem,
    ).apply(lambda args: encode_tls_secret_data(args[0], args[1])),
    opts=OPTS,
)

secrets_file_path = Path(__file__).parent / "secrets" / "langfuse.yaml"
salt_secret = fill_in_password(encrypted_yaml=secrets_file_path, value_path="salt")
nextauth_secret = fill_in_password(
    encrypted_yaml=secrets_file_path, value_path="nextauth"
)

values_file_path = Path(__file__).parent / "values" / "langfuse.yaml"
with open(values_file_path, "r") as f:
    chart_values = yaml.safe_load(f)

    def prepare_values(
        nextauth,
        salt,
    ) -> Dict[str, str]:
        return {
            "nextauth": nextauth,
            "salt": salt,
        }

    values = Output.all(
        nextauth_secret["nextauth"],
        salt_secret["salt"],
    ).apply(
        lambda args: prepare_values(
            args[0],
            args[1],
        )
    )

    chart_values["langfuse"]["nextauth"]["secret"]["value"] = values["nextauth"]
    chart_values["langfuse"]["salt"]["value"] = values["salt"]

langfuse_release = k8s.helm.v3.Release(
    "langfuse",
    k8s.helm.v3.ReleaseArgs(
        chart="langfuse",
        version="1.2.18",
        name="langfuse",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://langfuse.github.io/langfuse-k8s",
        ),
        namespace=langfuse_ns.metadata["name"],
        values=chart_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider_par_2,
        depends_on=[langfuse_ns, langfuse_tls_secret],
    ),
)
